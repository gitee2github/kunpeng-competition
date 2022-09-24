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

from datetime import datetime
import enum
import subprocess
from oslo_config import cfg


from hostha.common.openstack import keystone
from hostha.common.openstack import nova
from hostha import context
from hostha.db import api as db_api


EV_HOST_HEALTH_UPDATE = 'host.health.update'
EV_HOST_EVACUATION_STARTED = 'host.evacuation.started'
EV_HOST_EVACUATION_FINISHED = 'host.evacuation.finished'
EV_VM_EVACUATION_STARTED = 'instance.evacuation.started'
EV_VM_EVACUATION_FINISHED = 'instance.evacuation.finished'

ALLOWED_EVACUATE_VM_STATE = ('ACTIVE', 'STOPPED', 'ERROR', 'UNMANAGED')

CONF = cfg.CONF


class HostTask(enum.Enum):
    RECOVERY = 'recovery'
    FENCE = 'consul-fence'  # fence host by consul
    IPMI = 'ipmi-fence'     # fence host by ipmi
    MIGRATE = 'migrate'     # migrate all instances away from the host
    EVACUATE = 'evacuate'   # evacuate all instances away from the host
    UNKNOWN = 'unknown'     # unknown
    DISABLED = 'disabled'   # diaabled


class ComputeHAException(Exception):
    def __init__(self, message=None):
        super(ComputeHAException, self).__init__(message)


class ConsulServerException(ComputeHAException):
    pass


class ConsulPortException(ComputeHAException):
    pass


class HostRecoveryException(ComputeHAException):
    pass


class HostRecovering(ComputeHAException):
    pass


class IPMIConfigureException(ComputeHAException):
    pass


class ConsulGetStateException(ComputeHAException):
    pass


# configuration db util
def get_configuration(group, name):
    ctx = context.get_admin_context()
    filters = {"group": group, "name": name}
    value = db_api.configuration_get_by_name(ctx, filters).get("value")
    return eval(value)


# ha_config db util
def get_ha_config():
    ctx = context.get_admin_context()
    value = db_api.ha_config_get(ctx)
    return eval(value)


# ha_host db util
def get_hosts_by_filters(filters):
    ctx = context.get_admin_context()
    return db_api.ha_host_get_by_filters(ctx, filters=filters)


def get_host_by_name(hostname):
    filters = {"hostname": hostname}
    return get_hosts_by_filters(filters)[0]


def get_hosts_ha_enabled():
    filters = {"host_ha_enabled": 1}
    return get_hosts_by_filters(filters)


def get_ha_host_task_stat(hostname):
    host = get_host_by_name(hostname)
    return host['task']


def get_ha_host_last_health(hostname):
    host = get_host_by_name(hostname)
    return host['last_health']


def update_ha_host_last_health(hostname, last_health):
    values = {}
    values['last_health'] = last_health
    id = get_host_by_name(hostname)['id']
    ctx = context.get_admin_context()
    db_api.ha_host_update(ctx, id=id, values=values)


def update_ha_host(hostname, task=None, host_ha_enabled=None):
    values = {}
    values['task'] = task
    if host_ha_enabled is not None:
        values["host_ha_enabled"] = host_ha_enabled
    id = get_host_by_name(hostname)['id']
    ctx = context.get_admin_context()
    db_api.ha_host_update(ctx, id=id, values=values)


# ha_host_evacuation db util
def host_evacuate_create(hostname):
    ctx = context.get_admin_context()
    values = {"hostname": hostname,
              "started_at": datetime.utcnow()}
    return db_api.ha_host_evacuation_create(ctx, values)["id"]


def host_evacuate_finish(host_evacuation_id):
    ctx = context.get_admin_context()
    values = {"finished_at": datetime.utcnow()}
    return db_api.ha_host_evacuation_update(ctx, host_evacuation_id,
                                            values)


def get_host_evacuation(host_evacuation_id):
    ctx = context.get_admin_context()
    return db_api.ha_host_evacuation_get_by_id(ctx, host_evacuation_id)


# host_vm_evacuation db util
def get_evacuate_vms(filters):
    ctx = context.get_admin_context()
    return db_api.host_vm_evacuation_get_by_filters(ctx, filters)


def instance_evacuate_create(vm_name, vm_uuid, hostname,
                             host_evacuation_id, origin_state):
    ctx = context.get_admin_context()
    values = {"vm_name": vm_name,
              "src_host": hostname,
              "vm_uuid": vm_uuid,
              "started_at": datetime.utcnow(),
              "host_op_id": host_evacuation_id,
              'retry_count': 1,
              'origin_state': origin_state
              }
    return db_api.host_vm_evacuation_create(ctx, values)["id"]


def instance_evacuate_finish(vm_name, hostname,
                             host_evacuation_id, vm_uuid):
    ctx = context.get_admin_context()
    values = {"vm_name": vm_name,
              "src_host": hostname,
              "vm_uuid": vm_uuid,
              "started_at": datetime.utcnow(),
              "host_op_id": host_evacuation_id}
    return db_api.host_vm_evacuation_create(ctx, values)["id"]


def host_vm_evacuate_update(vm_evacuation_id, result, error_message,
                            hostname):
    ctx = context.get_admin_context()
    values = {"result": result,
              "message": error_message,
              "des_host": hostname,
              "finished_at": datetime.utcnow()}
    return db_api.host_vm_evacuation_update(ctx, vm_evacuation_id, values)


def host_vm_evacuate_update_retry_cnt(vm_evacuation_id, retry_cnt):
    ctx = context.get_admin_context()
    values = {"retry_count": retry_cnt}
    return db_api.host_vm_evacuation_update(ctx, vm_evacuation_id, values)


def get_host_power_state(ipmi_ip, ipmi_user, ipmi_password):
    if CONF.compute_ha.use_ipmitool:
        try:
            cmd = "ipmitool -R 1 -N 1 -I lanplus -H %s -U %s -P %s power " \
                  "status" % (ipmi_ip, ipmi_user, ipmi_password)
            output = subprocess.check_output(cmd.split())
            if 'on' in output:
                return 'on'
            elif 'off' in output:
                return 'off'
            else:
                return 'unknown'
        except Exception:
            raise


def set_host_power_state(ipmi_ip, ipmi_user, ipmi_password, power_state='off'):
    if CONF.compute_ha.use_ipmitool:
        try:
            cmd = "ipmitool  -R 1 -N 1 -I lanplus -H %s -U %s -P %s power" \
                  " %s" % (ipmi_ip, ipmi_user, ipmi_password, power_state)
            subprocess.check_output(cmd.split())
            return
        except Exception:
            raise


def get_nova_hypervisor_list():
    nova_ctx = get_ctx_admin()
    return nova.hypervisor_list(nova_ctx)


def get_nova_host_list():
    nova_ctx = get_ctx_admin()
    hosts = nova.host_list(nova_ctx)
    return hosts


def disable_compute_service(hostname):
    nova_ctx = get_ctx_admin()
    return nova.disable_compute_service(nova_ctx, hostname)


def force_down_compute_service(hostname, forced_down=True):
    nova_ctx = get_ctx_admin()
    return nova.service_force_down(nova_ctx,
                                   host=hostname,
                                   binary='nova-compute',
                                   forced_down=forced_down)


def get_host_instances(hostname):
    nova_ctx = get_ctx_admin()
    hypervisor = nova.hypervisor_servers(nova_ctx, hostname)
    if "servers" in hypervisor:
        instances = [server['uuid'] for server in hypervisor["servers"]]
    else:
        instances = []
    return instances


def get_instance_details(instance_uuid):
    nova_ctx = get_ctx_admin()
    return nova.server_details(nova_ctx, instance_uuid)


def evacuate_instance(instance_uuid, target_host):
    nova_ctx = get_ctx_admin()
    return nova.server_evacuate(nova_ctx, instance_uuid, target_host)


def reset_state_instance(instance_uuid, state):
    nova_ctx = get_ctx_admin()
    data = {
            "os-resetState": {
                "state": state
            }
        }
    return nova.instance_action(nova_ctx, instance_uuid, data)


def migrate_instance(instance_uuid):
    nova_ctx = get_ctx_admin()
    return nova.server_migrate(nova_ctx, instance_uuid)


def live_migrate_instance(instance_uuid):
    nova_ctx = get_ctx_admin()
    return nova.server_migrate_live(nova_ctx, instance_uuid)


def get_ctx_admin():
    try:
        ctx = keystone.generate_context(with_db_session=False)
        return ctx
    except Exception:
        raise
