# coding: utf8
# Copyright (c) 2021 Archeros Inc.
# hostha is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the
# Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import consul
import datetime
import eventlet
import socket
from subprocess import Popen, PIPE
import time

from oslo_config import cfg
from oslo_log import log
import oslo_messaging as messaging
from oslo_service import service
from oslo_utils import timeutils


from hostha.hostha import util

CONSUL_OPTS = [
    cfg.StrOpt("consul_servers",
               default=None,
               help="List of consul servers' addr sub-list. In one server's "
                    "addr sub-list, first manage addr, second tenant addr, "
                    "then storage addr; If using SAN, the storage addr is "
                    "not necessary. The number of consul servers numbers "
                    "should match the list lenth.  Config Example: "
                    "[['10.21.1.51', '192.168.20.51'],..."),
    cfg.StrOpt("consul_ports",
               default=[8500, 8900, 9300],
               help="consul_port is to access consul instance in the "
                    "controller node, first is the manage, second is "
                    "tenant, third is storage"),
    cfg.IntOpt("max_evacuation",
               default=3,
               help="The max number of host evacuations once time. "
                    "If failed nodes over this vlue, do no recovery."),
    cfg.BoolOpt("host_ipmi_enabled",
                default=True,
                help="This option enables or disables ipmi when do host "
                     "recovery. If there are no ipmi configurations for "
                     "hosts, please set this value False. Default value "
                     "is True."),
    cfg.BoolOpt("multiple_recovery",
                default=False,
                help="This option enables or disables multiple node "
                     "recovery."),
    cfg.IntOpt("wait_for_evacuation",
               default=60,
               help="The seconds to wait before evacuate instances."),
    cfg.IntOpt("interval_to_check_powerstate",
               default=3,
               help="Interval to check powerstate when fence host."),
    cfg.IntOpt("retry_to_check_powerstate",
               default=20,
               help="Retry to check powerstate when fence host."),
    cfg.IntOpt("evacuate_retry_count",
               default=3,
               help="Retry count if failed."),
    cfg.IntOpt("use_ipmitool",
               default=True,
               help="use ipmitool or pyghmi."),
    cfg.IntOpt("ipmi_check_interval",
               default=60,
               help="ipmi check interval")
]

CONF = cfg.CONF
CONF.register_opts(CONSUL_OPTS, group="compute_ha")

LOG = log.getLogger(__name__)


# consul network states and actions due to the network states.
# mgmt_network, tenant_network, storage_network, actions
# '0' means down, '1' means 'up'
# actions is list of ipmi, fence, migrate, evacuate, email...
consul_actions_matrix_3 = [
    [1, 1, 1, ['email']],
    [1, 1, 0, ['email', 'fence', 'evacuate']],
    [1, 0, 1, ['email', 'disabled']],
    [1, 0, 0, ['email', 'fence', 'evacuate']],
    [0, 1, 1, ['email']],
    [0, 1, 0, ['email', 'fence', 'evacuate']],
    [0, 0, 1, ['email', 'fence', 'evacuate']],
    [0, 0, 0, ['email', 'ipmi', 'evacuate']],
]
# consul network states and actions due to the network states.
# mgmt_network, tenant_network, actions
# '0' means down, '1' means 'up'
# actions is list of ipmi, fence, migrate, evacuate, email...
consul_actions_matrix_2 = [
    [1, 1, []],
    [1, 0, ['migrate']],
    [0, 1, ['email']],
    [0, 0, ['ipmi', 'evacuate']],
]


class HostCheckManager(service.Service):

    def __init__(self):
        super(HostCheckManager, self).__init__()
        self.consul_client = HealthMatrix(eval(CONF.compute_ha.consul_servers),
                                          eval(CONF.compute_ha.consul_ports))
        self.hostname = socket.gethostname()
        self.check_interval = CONF.compute_ha.host_check_interval
        self.check_retry = CONF.compute_ha.host_check_retry
        self.max_evacuation = CONF.compute_ha.max_evacuation
        self.least_gap_for_email = 3 * self.check_interval * self.check_retry
        self.ipmi_enabled = CONF.compute_ha.host_ipmi_enabled
        self.multiple_recovery = CONF.compute_ha.multiple_recovery
        self.wait_for_evacuation = CONF.compute_ha.wait_for_evacuation
        self.check_data = {}
        self.ipmi_check_data = {}
        self.check_nodes = {}
        self.ha_enabled_hosts = []
        self._notifier = None

    def _get_notifier(self):
        if not self._notifier:
            transport = messaging.get_transport(cfg.CONF)
            self._notifier = messaging.Notifier(
                transport,
                driver="messagingv2",
                topic="hostha-hostha-notification"
            )
        return self._notifier

    def send_notification(self, event_suffix, event_type, payload):
        notifier = self._get_notifier()
        if event_suffix.endswith("error"):
            method = notifier.error
        else:
            method = notifier.info
        try:
            method(ctxt={}, event_type=event_type, payload=payload)
            LOG.debug("Send notification %s", str(payload))
        except Exception as e:
            LOG.warn("Error send notification %s", str(e))

    def update_ha_hosts(self):
        try:
            ha_enabled_hosts = util.get_hosts_ha_enabled()
            self.ha_enabled_hosts = ha_enabled_hosts
        except Exception as e:
            LOG.warn("Update ha hosts error: %s", str(e))

    def get_ha_host_by_hostname(self, hostname):
        for ha_host in self.ha_enabled_hosts:
            if hostname == ha_host['hostname']:
                return ha_host

    def update_check_nodes(self):
        """Update all node int the cloud env

        It will check which nodes are controller-only, which nodes
        are compute-only, and which nodes are multiple nodes.
        It will sync with nova every 30 minutes, so it will
        reduce the calls of nova APIs.
        """
        try:
            all_hypervisors = util.get_nova_hypervisor_list()
            all_hosts = util.get_nova_host_list()
        except Exception as e:
            LOG.warn("Update hosts with nova error: %s", str(e))

        compute_nodes = [hypervisor['hypervisor_hostname'] for
                         hypervisor in all_hypervisors]
        controller_nodes = []
        for host in all_hosts:
            if host["service"] != "compute" and host["host_name"] not \
                    in controller_nodes:
                controller_nodes.append(host["host_name"])

        compute_only_nodes = []
        controller_only_nodes = []
        multiple_nodes = []
        for node in compute_nodes:
            if node not in controller_nodes:
                compute_only_nodes.append(node)
        for node in controller_nodes:
            if node not in compute_nodes:
                controller_only_nodes.append(node)
            else:
                multiple_nodes.append(node)

        self.check_nodes['compute-only'] = compute_only_nodes
        self.check_nodes['controller-only'] = controller_only_nodes
        self.check_nodes['multiple'] = multiple_nodes

        LOG.info(self.check_nodes)

    def get_all_controller_nodes(self):
        return (self.check_nodes['multiple'] +
                self.check_nodes['controller-only'])

    def get_available_controller_nodes(self):
        all_hypervisors = util.get_nova_hypervisor_list()
        multiple_nodes = self.check_nodes['multiple']
        available_multiple_nodes = []
        for hypervisor in all_hypervisors:
            hypervisor_hostname = hypervisor['hypervisor_hostname']
            host_task_stat = util.get_ha_host_task_stat(hypervisor_hostname)
            if host_task_stat is None:
                if hypervisor_hostname in multiple_nodes:
                    available_multiple_nodes.append(hypervisor_hostname)

        return available_multiple_nodes + self.check_nodes['controller-only']

    def normalize_host_health(self, host_health, consul_host_map):
        normalized_host_health = []
        # '0' means down, '1' means 'up'
        # management network health
        if 'management' in host_health:
            normalized_host_health.append(0)
        else:
            normalized_host_health.append(1)
        # tenant network health
        if 'tenant' in host_health:
            normalized_host_health.append(0)
        else:
            normalized_host_health.append(1)
        # storage network health
        if 'storage' in consul_host_map:
            if 'storage' in host_health:
                normalized_host_health.append(0)
            else:
                normalized_host_health.append(1)

        return normalized_host_health

    def delete_check_data(self):
        for hostname in self.check_data.keys():
            del self.check_data[hostname][:]

    def get_host_health_by_history(self, hostname):
        host_health_history = self.check_data.get(hostname)
        if not host_health_history or len(host_health_history) < \
                self.check_retry:
            LOG.debug("There is not enough check data for host %s." % hostname)
            return None

        host_health = []
        host_network_health_history = zip(*host_health_history)
        for i in range(0, len(host_network_health_history)):
            host_health.append(int(any(host_network_health_history[i])))

        return host_health

    def update_check_data(self):
        """update consul check data to cache"""

        LOG.info("update consul check data.")
        try:
            hosts_health = self.consul_client.getHealth(dcheck=True)
            LOG.debug("Consul update check data: %s.", str(hosts_health))
            consul_hosts_map = self.consul_client.getNodeList()
            for hostname in consul_hosts_map.keys():
                if hostname not in self.check_data:
                    self.check_data[hostname] = []
                # add new check data in cache
                host_health = hosts_health.get(hostname, [])
                consul_host_map = consul_hosts_map.get(hostname)
                normalized_host_health = self.normalize_host_health(
                    host_health, consul_host_map)
                self.check_data[hostname].append(normalized_host_health)
                # delete old check data in cache
                if len(self.check_data[hostname]) > self.check_retry:
                    del(self.check_data[hostname][0])
        except Exception as e:
            LOG.exception("update consul check data error: %s", str(e))
            self.delete_check_data()

    def delete_ipmi_check_data(self):
        for hostname in self.ipmi_check_data.keys():
            del self.ipmi_check_data[hostname][:]

    def get_host_ipmi_connection(self, host):
        try:
            self.check_host_ipmi_configuration(host)
            util.get_host_power_state(host['ipmi_ip'],
                                      host['ipmi_user'],
                                      host['ipmi_password'])
        except Exception:
            return 0
        else:
            return 1

    def update_ipmi_check_data(self):
        '''update ipmi connection check to cache'''
        LOG.info("update ipmi check data.")
        try:
            for host in self.ha_enabled_hosts:
                hostname = host["hostname"]
                # not allown the node do itself check
                if hostname == self.hostname:
                    continue
                if hostname not in self.ipmi_check_data:
                    self.ipmi_check_data[hostname] = []
                # add new check data in cache
                host_ipmi_connection = self.get_host_ipmi_connection(host)
                self.ipmi_check_data[hostname].append(host_ipmi_connection)
                # delete old check data in cache
                if len(self.ipmi_check_data[hostname]) > self.check_retry:
                    del(self.ipmi_check_data[hostname][0])
        except Exception as e:
            LOG.exception("update ipmi check data error: %s", str(e))
            self.delete_ipmi_check_data()
        LOG.info('ipmi data %s' % self.ipmi_check_data)

    def get_consul_actions(self, host_health):
        """Choice actions form consul_actions_matrix by current health"""
        mgmt_net_state = host_health[0]
        storage_net_state = host_health[1]
        if len(host_health) == 3:
            tenant_net_state = host_health[2]
            for consul_actions in consul_actions_matrix_3:
                if ((mgmt_net_state == consul_actions[0]) and
                        (storage_net_state == consul_actions[1]) and
                        (tenant_net_state == consul_actions[2])):
                    return consul_actions[3]
        if len(host_health) == 2:
            for consul_actions in consul_actions_matrix_2:
                if ((mgmt_net_state == consul_actions[0]) and
                        (storage_net_state == consul_actions[1])):
                    return consul_actions[2]

    def do_host_recovery(self, hostname):
        host_health = self.get_host_health_by_history(hostname)
        if host_health is None:
            return

        try:
            LOG.debug("Host %s recovery is executed by %s.",
                      hostname, self.hostname)
            self.recovery_actions_execute(hostname, host_health)
        except util.HostRecovering as e:
            LOG.debug("Host recovering, %s.", str(e))
        except util.IPMIConfigureException as e:
            if self.ipmi_enabled:
                LOG.exception("Host recovery failed, %s.", str(e))
        except util.HostRecoveryException as e:
            LOG.exception("Host recovery failed, %s.", str(e))
        except Exception as e:
            LOG.exception("Host recovery failed, %s.", str(e))

    def get_failure_compute_nodes(self):
        failure_nodes = []
        for host in self.ha_enabled_hosts:
            hostname = host["hostname"]
            if hostname not in self.check_nodes['controller-only']:
                host_health = self.get_host_health_by_history(hostname)
                if host_health is None:
                    continue
                if not any(host_health):
                    failure_nodes.append(hostname)

        return failure_nodes

    def do_recovery(self):
        LOG.info("Do host recovery.")

        # If failure compute nodes over max evacuation, not do recovery.
        failure_compute_nodes = self.get_failure_compute_nodes()
        if len(failure_compute_nodes) > self.max_evacuation:
            LOG.info("Skip recovery, because current failure nodes exceed "
                     "max evacuation. Failed compute nodes: %s",
                     failure_compute_nodes)
            return

        try:
            for host in self.ha_enabled_hosts:
                hostname = host["hostname"]
                # not allown the node do itself recovery
                if hostname != self.hostname:
                    gt = eventlet.spawn(self.do_host_recovery, hostname)
                    gt.wait()
        except Exception as e:
            LOG.exception("Do host recovery error: %s", str(e))

    def start(self):
        LOG.info("Consul Host Check Manager start...")
        self.update_check_nodes()
        self.update_ha_hosts()
        self.update_ipmi_check_data()
        self.tg.add_timer(1800, self.update_check_nodes, 0)
        self.tg.add_timer(self.check_interval, self.update_ha_hosts, 0)
        self.tg.add_timer(CONF.compute_ha.ipmi_check_interval,
                          self.update_ipmi_check_data,
                          0)
        self.tg.add_timer(self.check_interval, self.update_check_data, 1)
        self.tg.add_timer(self.check_interval, self.update_recovery, 3)
        self.tg.add_timer(self.check_interval, self.do_recovery, 2).wait()

    def update_recovery(self):
        LOG.info("update host recovery.")
        try:
            self.update_host_task_stat()
        except Exception as e:
            LOG.exception("update host recovery error: %s", str(e))

    def update_host_task_stat(self):
        for host in self.ha_enabled_hosts:
            hostname = host["hostname"]
            host_task_stat = host["task"]
            if host_task_stat is None:
                continue

            host_health = self.get_host_health_by_history(hostname)
            if host_health is None:
                continue

            if all(host_health):
                LOG.info('host_task_stat is %s, will reset' % host_task_stat)
                util.force_down_compute_service(hostname, forced_down=False)
                util.update_ha_host(hostname, None)

    def check_host_ipmi_configuration(self, host):
        hostname = host['hostname']
        if not all([host['ipmi_ip'], host['ipmi_user'],
                    host['ipmi_password']]):
            message = "Not enough ipmi configurations for host %s." % hostname
            raise util.IPMIConfigureException(message)

    def recovery_actions_execute(self, hostname, host_health):
        host = self.get_ha_host_by_hostname(hostname)
        actions = self.get_consul_actions(host_health)
        if 'email' in actions:
            self.email_host_health(hostname, host_health)
        if all(host_health):
            return

        host_task_stat = util.get_ha_host_task_stat(hostname)
        if host_task_stat is not None:
            return

        # To both controller and compute host, recovery if configration.
        # But if the active controller will be less than 1/2, stop recovery
        # for multi-hosts.
        # Pre-supposition: the number of controller nodes is odd.
        if hostname in self.check_nodes['multiple']:
            if not self.multiple_recovery:
                LOG.info("Host %s is a controller node, skip host recovery.",
                         hostname)
                return
            else:
                all_controllers_len = len(self.get_all_controller_nodes())
                available_controllers_len = len(
                    self.get_available_controller_nodes())
                if available_controllers_len - 1 < all_controllers_len/2 + 1:
                    LOG.info("The cloud env may be not available, so host %s "
                             "will not do host recovery.", hostname)
                    return

        LOG.info('host health for %s is %s' % (hostname, host_health))
        for action in actions:
            if action == 'evacuate':
                self.evacuate_action(hostname)
            if action == 'migrate':
                self.migrate_action(hostname)
            if action == 'ipmi':
                self.ipmi_action(host)
            if action == 'fence':
                self.fence_action(host, host_health)
            if action == 'disabled':
                self.disabled_action(hostname)

    def _wait_for_poweroff(self, host, sleep, retry):
        power_state = util.get_host_power_state(host['ipmi_ip'],
                                                host['ipmi_user'],
                                                host['ipmi_password'])
        while (power_state != 'off' and retry):
            time.sleep(sleep)
            power_state = util.get_host_power_state(
                host['ipmi_ip'],
                host['ipmi_user'],
                host['ipmi_password'])
            retry -= 1
        if not retry:
            return False
        return True

    def disabled_action(self, hostname):
        host_task_stat = util.get_ha_host_task_stat(hostname)
        if host_task_stat == util.HostTask.DISABLED.value:
            message = "host %s compute service is disabled" % hostname
            raise util.HostRecovering(message)

        util.update_ha_host(hostname, util.HostTask.DISABLED.value)
        util.disable_compute_service(hostname)

    def fence_action(self, host, host_health):
        hostname = host['hostname']
        self.check_host_ipmi_configuration(host)

        host_task_stat = util.get_ha_host_task_stat(hostname)
        if host_task_stat == util.HostTask.FENCE.value:
            message = "host %s is fencing by consul" % hostname
            raise util.HostRecovering(message)

        util.update_ha_host(hostname, util.HostTask.FENCE.value)

        cluster = None
        if host_health[0]:
            cluster = self.consul_client.con_m
        elif host_health[1]:
            cluster = self.consul_client.con_t
        elif len(host_health) > 2 and host_health[2]:
            cluster = self.consul_client.con_s

        if not cluster:
            self.ipmi_action(host)
        else:
            LOG.info("Try to fence host %s by consul.", hostname)
            fence_body = "fence@%s@%s" % (self.hostname, int(time.time()))
            self.consul_client.sendEvent(name="fence",
                                         node=hostname,
                                         body=fence_body,
                                         consulCluster=cluster)

            # if host not poweroff a time after consul fence,
            # then fence by ipmi.
            try:
                if self._wait_for_poweroff(
                        host,
                        CONF.compute_ha.interval_to_check_powerstate,
                        CONF.compute_ha.retry_to_check_powerstate):
                    LOG.info("Fence host %s by consul success.", hostname)
                else:
                    LOG.warn("Fence host %s by consul timeout,"
                             " try fence by ipmi",
                             hostname)
                    self.ipmi_action(host, check_host_stat=False)
            except Exception as e:
                LOG.exception("Can't get %s power state, error: %s.",
                              hostname, str(e))
                if any(self.ipmi_check_data[hostname]):
                    LOG.info('ipmi check data %s, ignore error' %
                             self.ipmi_check_data[hostname])
                    return

                # 3个网都断的情况才skip
                host_health = self.get_host_health_by_history(hostname)
                LOG.info('host health %s' % host_health)
                if any(host_health):
                    LOG.error(
                        'not all port are down, and can not get ipmi,'
                        'please check error')
                    raise e
                else:
                    LOG.info('all net are down, ignore error')
                    return

    def ipmi_action(self, host, check_host_stat=True):
        hostname = host['hostname']
        self.check_host_ipmi_configuration(host)

        host_task_stat = util.get_ha_host_task_stat(hostname)
        if host_task_stat == util.HostTask.IPMI.value:
            message = "host %s is fencing by ipmi" % hostname
            raise util.HostRecovering(message)

        util.update_ha_host(hostname, util.HostTask.IPMI.value)

        try:
            power_state = util.get_host_power_state(host['ipmi_ip'],
                                                    host['ipmi_user'],
                                                    host['ipmi_password'])
        except Exception as e:
            LOG.exception("Can't get %s power state, error: %s.",
                          hostname, str(e))
            # Disconnect for now, but if ipmi connect before,
            # just skip ipmi fence
            if any(self.ipmi_check_data[hostname]):
                LOG.info('ipmi check data %s, ignore error' %
                         self.ipmi_check_data[hostname])
                return

            # only skip when all net down
            host_health = self.get_host_health_by_history(hostname)
            LOG.info('host health %s' % host_health)
            if any(host_health):
                LOG.error('not all port are down, and can not get ipmi,'
                          'please check error')
                raise e
            else:
                LOG.info('all net are down, ignore error')
                return

        if power_state == 'off':
            LOG.info("Host %s is power-off, pass ipmi-Fence.", hostname)
            return

        LOG.info("Try to fence host %s by ipmi.", hostname)
        util.set_host_power_state(host['ipmi_ip'],
                                  host['ipmi_user'],
                                  host['ipmi_password'],
                                  'off')

        if self._wait_for_poweroff(
                host,
                CONF.compute_ha.interval_to_check_powerstate,
                CONF.compute_ha.retry_to_check_powerstate):
            LOG.info("Fence host %s by ipmi success.", hostname)
        else:
            message = "Fence host %s by ipmi timeout."
            raise util.HostRecoveryException(message)

    def evacuate_action(self, hostname):
        host_task_stat = util.get_ha_host_task_stat(hostname)
        if host_task_stat == util.HostTask.EVACUATE.value:
            message = "host %s is evacuating" % hostname
            raise util.HostRecovering(message)

        util.update_ha_host(hostname, util.HostTask.EVACUATE.value)

        # because most services set 60s  timeout,
        # wait for a while before evacuate instances.
        if self.wait_for_evacuation > 0:
            time.sleep(self.wait_for_evacuation)

        instance_uuid_list = util.get_host_instances(hostname)
        if not len(instance_uuid_list):
            LOG.info("There is no VM running in host %s, just pass "
                     "host evacuate!", hostname)
            return

        LOG.info("Try to evacuate host %s.", hostname)
        util.force_down_compute_service(hostname, forced_down=True)

        host_evacuation_id = util.host_evacuate_create(hostname)
        payload = {"hostname": hostname, "id": host_evacuation_id,
                   "time": timeutils.utcnow()}
        self.send_notification("notifier.info",
                               util.EV_HOST_EVACUATION_STARTED,
                               payload)

        response = []
        for instance_uuid in instance_uuid_list:
            try:
                instance = util.get_instance_details(instance_uuid)
                instance_name = instance["name"]
                vm_state = instance['status']
                pwr_state = instance['OS-EXT-STS:power_state']
                if vm_state not in util.ALLOWED_EVACUATE_VM_STATE:
                    LOG.info('skip evacuate vm %s because vm in %s state'
                             % (instance_name, vm_state))
                    continue
            except Exception as e:
                LOG.exception("Get vm %s details error: %s",
                              instance_uuid, str(e))
                continue

            LOG.info("Start to evacuate VM %s from host %s.",
                     instance_name, hostname)
            vm_evacuation_id = util.instance_evacuate_create(
                instance_name,
                instance_uuid,
                hostname,
                host_evacuation_id,
                pwr_state
            )
            payload = {
                "host_evacuation_id": host_evacuation_id,
                "instance_name": instance_name,
                "instance_id": instance_uuid,
                "time": timeutils.utcnow(),
                "hostname": hostname,
                "source": hostname,
                "destination": "",
                "id": vm_evacuation_id}
            self.send_notification(
                "notifer.info", util.EV_VM_EVACUATION_STARTED, payload)
            error_message = ""
            try:
                util.evacuate_instance(instance_uuid, target_host=None)
                response.append({"server_uuid": instance_uuid,
                                 "evacuate_accepted": 1,
                                 "error_message": error_message[:250]})
            except Exception as e:
                LOG.exception("Can't evacuate vm %s, error:%s",
                              instance_name, str(e))
                gt = eventlet.spawn(self.retry_evacuate, instance_uuid,
                                    vm_evacuation_id, host_evacuation_id,
                                    hostname, instance_name)
                gt.wait()

    def migrate_action(self, hostname):
        host_task_stat = util.get_ha_host_task_stat(hostname)
        if host_task_stat == util.HostTask.MIGRATE.value:
            LOG.debug("Host %s is migrating, pass host migration", hostname)
            return
        else:
            LOG.info("Start to migrate host %s", hostname)
            util.update_ha_host(hostname,
                                util.HostTask.MIGRATE.value)

        instance_uuid_list = util.get_host_instances(hostname)
        if not len(instance_uuid_list):
            LOG.info("There is no VM running in host %s, just pass "
                     "host migrate!", hostname)
            return

        util.disable_compute_service(hostname)
        for instance_uuid in instance_uuid_list:
            instance = util.get_instance_details(instance_uuid)
            try:
                LOG.info("Start to migrate VM %s from host %s.",
                         instance_uuid, hostname)
                if instance['status'] == 'ACTIVE':
                    util.live_migrate_instance(instance_uuid)
                else:
                    util.migrate_instance(instance_uuid)
            except Exception as e:
                LOG.exception("Can't migrate vm %s, error:%s",
                              instance_uuid, str(e))

    def email_host_health(self, hostname, host_health):
        """email host health

        Email host health when any of the host management/tenant/storage
        is down. If the status continues, it will send one notification
        per hour.
        """

        current_time = timeutils.utcnow()
        host = self.get_ha_host_by_hostname(hostname)
        last_health = host['last_health']
        if last_health:
            last_report_health = last_health['health']
            last_report_time = timeutils.parse_strtime(last_health['time'])
            if all(last_report_health) and all(host_health):
                return
            if (host_health == last_report_health and
                    last_report_time + datetime.timedelta(hours=1) >
                    current_time):
                return
            if last_report_time + datetime.timedelta(
                    seconds=self.least_gap_for_email) > current_time:
                return

        last_health = {}
        last_health['health'] = host_health
        last_health['time'] = current_time
        util.update_ha_host_last_health(hostname, last_health)

        payload = {"hostname": hostname,
                   "time": timeutils.utcnow(),
                   "manage_network": 'UP' if host_health[0] else 'DOWN',
                   "tenant_network": 'UP' if host_health[1] else 'DOWN',
                   "storage_network": 'UP' if host_health[2] else 'DOWN',
                   "id": '0000',
                   }
        self.send_notification("notifier.info",
                               util.EV_HOST_HEALTH_UPDATE,
                               payload)

    # api retry
    def retry_evacuate(self, vmid, ev_id, host_ev_id, hostname, instance_name):
        cnt = 1
        while cnt < CONF.compute_ha.evacuate_retry_count:
            try:
                time.sleep(10)
                cnt += 1
                util.evacuate_instance(vmid, target_host=None)
                util.host_vm_evacuate_update_retry_cnt(ev_id, cnt)
                LOG.info('succ send api for %s' % vmid)
                break
            except Exception as e:
                util.host_vm_evacuate_update_retry_cnt(ev_id, cnt)
                LOG.exception("Can't evacuate vm error:%s" % str(e))

            # set state when retry failed
            if cnt == CONF.compute_ha.evacuate_retry_count:
                LOG.info('after %s retry, still can not evacuate vm %s' %
                         (CONF.compute_ha.evacuate_retry_count, instance_name))
                util.host_vm_evacuate_update(ev_id,
                                             0,
                                             str(e)[:250],
                                             hostname)
                payload = {
                    "host_evacuation_id": host_ev_id,
                    "instance_name": instance_name,
                    "instance_id": vmid,
                    "time": timeutils.utcnow(),
                    "hostname": hostname,
                    "source": hostname,
                    "destination": "",
                    "succeeded": False,
                    "message": str(e)[:250],
                    "id": ev_id}
                self.send_notification("notifier.info",
                                       util.EV_VM_EVACUATION_FINISHED,
                                       payload)


class HealthMatrix(object):
    # we assume that controller IP is mapping with port one by one
    # The first is management, second is Tenant, third is storage
    def __init__(self, controllers=None, ports=[8500, 8900, 9300]):
        self.hostname = socket.gethostname()
        self.hostip = socket.gethostbyname(self.hostname)
        self.controller_check(controllers, ports)
        self.controllers = controllers
        self.ports = ports
        self.hasStorage = False
        self.Nodes = {}
        # Management Network
        self.con_m = consul.Consul(host=self.controllerip[0], port=ports[0])
        # Tenant Network
        self.con_t = consul.Consul(host=self.controllerip[1], port=ports[1])
        if len(self.controllerip) == 3:
            self.hasStorage = True
            self.con_s = consul.Consul(host=self.controllerip[2],
                                       port=ports[2])

    def controller_check(self, controller_ip=None, ports=[8500, 8900, 9300]):
        if not controller_ip or type(controller_ip) != list:
            message = "Consul server config error."
            raise util.ConsulServerException(message)

        for controller in range(len(controller_ip)):
            if ((len(controller_ip[controller]) < 2) or
                    (len(controller_ip[controller]) > 3)):
                message = ("error, too many/less consul controler network, %d",
                           controller_ip[controller])
                raise util.ConsulServerException(message)
            if self.hostip in controller_ip[controller]:
                self.controllerip = controller_ip[controller]
        if len(ports) < 2 or len(ports) > 3:
            message = "error, too many/less ports, %s" % ports
            raise util.ConsulPortException(message)

    # all defalt consul is management network
    def getKVlib(self, key, consulCluster=None):
        if consulCluster is None:
            return self.con_m.kv.get(key)

        return consulCluster.kv.get(key)

    def putKVlib(self, key, value, consulCluster=None):
        if consulCluster is None:
            return self.con_m.kv.put(key, value)

        return consulCluster.kv.put(key, value)

    def deleteKVlib(self, key, consulCluster=None):
        if consulCluster is None:
            return self.con_m.kv.delete(key)

        return consulCluster.kv.delete(key)

    def sendEvent(self, name="test", node=None, body="", consulCluster=None):
        if consulCluster is None:
            event = self.con_m.event
            return event.fire(name=name, node=node, body=body)

        return consulCluster.event.fire(name=name, node=node, body=body)

    # Nodes = {'hostname1':{'management':'192.168.20.51',
    #                       'tenant':'10.168.20.51',
    #                       'storage':'172.168.20.51'}}
    def _getNodeList(self, cluster='management'):
        if cluster == 'management':
            consulCluster = self.con_m
        elif cluster == 'storage' and self.hasStorage:
            consulCluster = self.con_s
        elif cluster == 'tenant':
            consulCluster = self.con_t
        else:
            return self.Nodes

        members = consulCluster.agent.members()
        for m in members:
            if m.get('Name') in self.Nodes.keys():
                if cluster not in self.Nodes.get(m.get('Name')).keys():
                    self.Nodes.get(m.get('Name')).setdefault(cluster,
                                                             m.get('Addr'))
            else:
                self.Nodes.setdefault(m.get('Name'), {cluster: m.get('Addr')})
        return self.Nodes

    def getNodeList(self):
        Nodes = {}
        for cl in ['management', 'storage', 'tenant']:
            Nodes = self._getNodeList(cluster=cl)
        return Nodes

    def getNodeState(self, node=None, consulCluster=None):
        if consulCluster is None:
            health = self.con_m.health
            return health.node(node=node)

        return consulCluster.health.node(node=node)

    def getState(self, state="any", consulCluster=None):
        status = []
        try:
            # health.state will return a truple, the first element is ID,
            # send element is the list of the state
            if consulCluster is None:
                health = self.con_m.health
                status = health.state(name=state)[1]
            else:
                status = consulCluster.health.state(name=state)[1]
        except Exception:
            cluster = "Management"
            if self.hasStorage and consulCluster == self.con_s:
                cluster = "Storage"
            if consulCluster == self.con_t:
                cluster = "Tenant"
            message = "Failed to get the health state of cluster %s" % cluster
            raise util.ConsulGetStateException(message)

        return status

    # [{u'Node': u'n1', u'CheckID': u'serfHealth',
    # u'Name': u'Serf Health Status',
    # u'ServiceName': u'', u'Notes': u'',
    # u'ModifyIndex': 254, u'Status': u'passing',
    # u'ServiceID': u'', u'ServiceTags': [],
    # u'Output': u'Agent alive and reachable',
    # u'CreateIndex': 5}]
    # we only prase critical state
    def praseState(self, health={}, state=[], cluster='management'):
        if state == []:
            return health

        for s in state:
            host = s.get('Node')
            checkID = s.get('CheckID')
            status = s.get('Status')

            # Check if the node in Nodes
            if ((host not in self.Nodes.keys()) or
                    (cluster not in self.Nodes.get(host).keys())):
                self._getNodeList(cluster)
            # we only prase critical state
            if status != 'critical':
                continue

            details = s.get('Output')
            # if no storage network, storage info will go through management
            # and tenant, but all checks must be with checkID 'storage_xxx'
            # if hasStorage is true we will ignore the storage checkID
            if 'storage' in checkID and self.hasStorage:
                continue

            if 'storage' in checkID:
                credit = True
                # when the cluster member it self is in critical mode
                # We assume that the storage check is unbelievable
                for i in range(len(state)):
                    checkIDSerf = state[i].get('CheckID')
                    statusSerf = state[i].get('Status')
                    if ('serfHealth' == checkIDSerf and
                            statusSerf == 'critical'):
                        credit = False
                        break
                # only the credit is true we could update the storage check
                if credit:
                    if host not in health.keys():
                        health.setdefault(host,
                                          {'storage': [status, details]})
                    elif 'storage' not in health[host].keys():
                        health.get(host).setdefault('storage',
                                                    [status, details])
            else:
                if host not in health.keys():
                    health.setdefault(host, {cluster: [status, details]})
                elif cluster not in health[host].keys():
                    health.get(host).setdefault(cluster, [status, details])

        return health

    def exec_common(self, command):
        handle = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        return handle

    # in case of consul client been killed, and report the error state,
    # we double check the error node using fping
    def doubleCheck(self, health={}):
        if health == {}:
            return health
        ip = ''
        for h in health.keys():
            for t in health.get(h).keys():
                # if it does not have storage network, we just skip check
                if self.hasStorage is False and t == 'storage':
                    continue
                if t not in self.Nodes.get(h).keys():
                    continue
                ip = ' '.join([ip, self.Nodes.get(h).get(t)])

        if ip == '':
            return health

            # check host by fping -r retry -q multi_ip
        command = "fping -u %s" % ip
        LOG.debug('command %s' % command)
        handle = self.exec_common(command)
        return_code = handle.wait()
        if return_code != 0:
            return_out = handle.stdout.read().strip().split('\n')
            for p in ip.strip().split(' '):
                # here means this IP os reachable, mark it as health
                # so we delete the Item in health
                if p not in return_out:
                    net_type = ''
                    host = ''
                    for n in self.Nodes.keys():
                        if host != '' and net_type != '':
                            break
                        for t in self.Nodes.get(n).keys():
                            if self.Nodes.get(n).get(t) == p:
                                net_type = t
                                host = n
                                break
                    if host != '' and net_type != '':
                        # we should not run here but we need check
                        if (host not in health.keys()) or \
                           (net_type not in health.get(host).keys()):
                            continue

                        health.get(host).pop(net_type)
                        if health.get(host) == {}:
                            health.pop(host)
        else:
            return {}

        return health

    # {"hostname":{"management":[status, details],
    #              "tenant":[status, details],
    #              "storage":[status, details]},
    # }
    def getHealth(self, dcheck=False):
        health = {}
        state_m = self.getState(state="critical", consulCluster=self.con_m)
        health = self.praseState(health, state_m, 'management')
        state_t = self.getState(state="critical", consulCluster=self.con_t)
        health = self.praseState(health, state_t, 'tenant')
        if self.hasStorage:
            state_s = self.getState(state="critical", consulCluster=self.con_s)
            health = self.praseState(health, state_s, 'storage')

        # need verify the reachable host by fping
        if dcheck:
            health = self.doubleCheck(health)

        return health
