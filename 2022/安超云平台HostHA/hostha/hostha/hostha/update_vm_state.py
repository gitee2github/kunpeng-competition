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
from oslo_config import cfg
from oslo_log import log
from oslo_service import service
import oslo_messaging as messaging
from oslo_utils import timeutils
import time
import eventlet

from hostha import context
from hostha.db import api as db_api
from hostha.hostha import util


LOG = log.getLogger(__name__)
CONF = cfg.CONF

EV_HOST_EVACUATION_STARTED = 'host.evacuation.started'
EV_HOST_EVACUATION_FINISHED = 'host.evacuation.finished'
EV_VM_EVACUATION_STARTED = 'instance.evacuation.started'
EV_VM_EVACUATION_FINISHED = 'instance.evacuation.finished'


def host_vm_evacuation_get_by_filters(ctx, filters=None):
    filters = {"result": None}
    return db_api.host_vm_evacuation_get_by_filters(ctx, filters)


def get_vm_count(ctx, filters):
    vms = db_api.host_vm_evacuation_get_by_filters(ctx, filters)
    count = len(vms)
    return count


def send_notification(event_suffix, event_type, payload):
    try:
        transport = messaging.get_transport(cfg.CONF)
        notifier = messaging.Notifier(transport,
                                      driver="messagingv2",
                                      topic="hostha-hostha-notification")
        if event_suffix.endswith("error"):
            method = notifier.error
        else:
            method = notifier.info
        method(ctxt={}, event_type=event_type, payload=payload)
    except Exception as e:
        LOG.warn("update vm state send notification %s", str(e))


def check_if_last(ctx, host_op_id, hostname):
    # when db data is null and host evacuate is end
    filters = {"host_op_id": host_op_id,
               "result": None}
    if not db_api.host_vm_evacuation_get_by_filters(ctx, filters):
        id = int(host_op_id)
        host_evacuate = util.get_host_evacuation(id)
        if host_evacuate.finished_at is None:
            util.host_evacuate_finish(id)
            suc_c = get_vm_count(ctx, {"host_op_id": host_op_id, "result": 1})
            fail_c = get_vm_count(ctx, {"host_op_id": host_op_id, "result": 0})
            payload = {"id": host_op_id, "hostname": hostname,
                       "time": str(datetime.utcnow()), "success": suc_c,
                       "failure": fail_c}
            send_notification("notifier.info",
                              EV_HOST_EVACUATION_FINISHED, payload)


def host_vm_recovery_get_by_filters(ctx, filters=None):
    filters = {"result": None}
    return db_api.host_vm_recovery_get_by_filters(ctx, filters)


def host_vm_recovery_update(ctx, id, result, error_message,
                            vm_node):
    values = {"result": result,
              "message": error_message,
              "finished_at": timeutils.utcnow(),
              "des_host": vm_node}
    return db_api.host_vm_recovery_update(ctx, id, values)


def get_exception_message(exception):
    message = ""
    if "message" in exception:
        message = str(exception["message"])[:250]
    elif "err" in exception:
        message = str(exception["err"])[:250]
    else:
        message = "Error Message not in standardized format, Please " \
                  "find compute log for message"
    return message


class NotificationEndpoint(object):
    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        # LOG.debug("in nova info payload %s", payload)
        # LOG.debug("in nova info event_type %s", event_type)
        # LOG.debug("in nova info metadata %s", metadata)
        # begin()
        # when get event rebuild.start
        # when get event rebuild.end
        # if event_type == "compute.instance.reboot.start":
        if event_type == "compute.instance.rebuild.start":
            ctx = context.get_admin_context()
            vm_list = host_vm_evacuation_get_by_filters(ctx)
            vm_uuid = payload["instance_id"]
            # vm_node = payload["node"]
            vm_node = str(publisher_id.split('.')[-1])
            if vm_uuid in [vm["vm_uuid"] for vm in vm_list]:
                LOG.info("instance %s task %s on %s", vm_uuid, event_type,
                         vm_node)
        # if event_type == "compute.instance.reboot.end":
        if event_type == "compute.instance.rebuild.end":
            ctx = context.get_admin_context()
            vm_list = host_vm_evacuation_get_by_filters(ctx)
            vm_uuid = payload["instance_id"]
            # vm_node = payload["node"]
            vm_node = str(publisher_id.split('.')[-1])
            for vm in vm_list:
                if vm_uuid == vm["vm_uuid"]:
                    LOG.info("instance %s task %s on %s", vm_uuid, event_type,
                             vm_node)
                    id = vm["id"]
                    result = 1
                    message = ""
                    util.host_vm_evacuate_update(id, result, message, vm_node)
                    payload = {"source": vm["src_host"],
                               "host_evacuation_id": vm['host_op_id'],
                               "instance_name": vm['vm_name'],
                               "destination": "",
                               "instance_id": vm_uuid,
                               "time": str(datetime.utcnow()),
                               "hostname": vm_node,
                               "succeeded": True, "message": message, "id": id}
                    send_notification("notifier.info",
                                      EV_VM_EVACUATION_FINISHED, payload)
                    check_if_last(ctx, vm['host_op_id'], vm["src_host"])
        # for vm recovery
        if event_type == "compute.instance.reboot.start":
            ctx = context.get_admin_context()
            vm_list = host_vm_recovery_get_by_filters(ctx)
            vm_uuid = payload["instance_id"]
            # vm_node = payload["node"]
            vm_node = str(publisher_id.split('.')[-1])
            if vm_uuid in [vm["vm_uuid"] for vm in vm_list]:
                LOG.info("instance %s task %s on %s", vm_uuid, event_type,
                         vm_node)
        if event_type == "compute.instance.reboot.end":
            ctx = context.get_admin_context()
            vm_list = host_vm_recovery_get_by_filters(ctx)
            vm_uuid = payload["instance_id"]
            # vm_node = payload["node"]
            vm_node = str(publisher_id.split('.')[-1])
            for vm in vm_list:
                if vm_uuid == vm["vm_uuid"]:
                    LOG.info("instance %s task %s on %s", vm_uuid, event_type,
                             vm_node)
                    id = vm["id"]
                    result = 1
                    message = ""
                    host_vm_recovery_update(ctx, id, result, message,
                                            vm_node)

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        if event_type == "compute.instance.rebuild.error":
            LOG.info("in nova error payload %s", payload)
            LOG.info("in nova error event_type %s", event_type)
            LOG.info("in nova error metadata %s", metadata)

            ctx = context.get_admin_context()
            vm_list = host_vm_evacuation_get_by_filters(ctx)
            # message = payload["exception"]["message"][:250]
            message = get_exception_message(payload["exception"])
            vm_uuid = payload["instance_id"]
            # vm_node = payload["node"]
            vm_node = str(publisher_id.split('.')[-1])
            for vm in vm_list:
                if vm_uuid == vm["vm_uuid"]:
                    LOG.info("instance %s task %s on %s", vm_uuid, event_type,
                             vm_node)
                    id = vm["id"]
                    if vm['retry_count'] == \
                            CONF.compute_ha.evacuate_retry_count:
                        result = 0
                        util.host_vm_evacuate_update(id, result,
                                                     message, vm_node)
                        payload = {"source": vm["src_host"],
                                   "host_evacuation_id": vm['host_op_id'],
                                   "instance_name": vm['vm_name'],
                                   "destination": "",
                                   "instance_id": vm_uuid,
                                   "time": str(datetime.utcnow()),
                                   "hostname": vm_node,
                                   "succeeded": False,
                                   "message": message, "id": id}
                        send_notification("notifier.info",
                                          EV_VM_EVACUATION_FINISHED, payload)
                        # reset vm state
                        reset_vm_state(vm)
                    else:
                        gt = eventlet.spawn(rebuild_again, vm)
                        gt.wait()
                check_if_last(ctx, vm['host_op_id'], vm['src_host'])

        # for vm recovery
        if event_type == "compute.instance.reboot.error":
            ctx = context.get_admin_context()
            vm_list = host_vm_evacuation_get_by_filters(ctx)
            # message = payload["exception"]["message"][:250]
            message = get_exception_message(payload["exception"])
            vm_uuid = payload["args"]["instance"]["uuid"]
            # vm_node = payload["args"]["instance"]["node"]
            vm_node = str(publisher_id.split('.')[-1])
            for vm in vm_list:
                if vm_uuid == vm["vm_uuid"]:
                    LOG.info("instance %s task %s on %s", vm_uuid, event_type,
                             vm_node)
                    id = vm["id"]
                    result = 0
                    util.host_vm_evacuate_update(id, result, message, vm_node)


# send again
def rebuild_again(vm):
    time.sleep(10)
    instance_uuid = vm["vm_uuid"]
    vm['retry_count'] += 1
    util.host_vm_evacuate_update_retry_cnt(vm['id'], vm['retry_count'])
    LOG.info('Start evacuate vm: %s, retried %s time' % (instance_uuid,
                                                         vm['retry_count']))
    util.evacuate_instance(instance_uuid, target_host=None)


def reset_vm_state(vm):
    LOG.debug('send reset state api for vm %s, origin state %s' %
              (vm['vm_name'], vm['origin_state']))
    instance_uuid = vm["vm_uuid"]
    origin_state = vm["origin_state"]

    if origin_state not in ['active', 'error']:
        origin_state = 'active'

    util.reset_state_instance(instance_uuid, origin_state)


class UpdateVmState(service.Service):
    def __init__(self):
        super(UpdateVmState, self).__init__()
        transport = messaging.get_notification_transport(cfg.CONF)
        targets = [messaging.Target(exchange="nova", topic="notifications")]
        endpoints = [NotificationEndpoint()]
        self.listener = messaging.get_notification_listener(
            transport, targets, endpoints,
            executor="blocking",
            pool="hostha-vmstate-updater")

    def start(self):
        LOG.info("Update Vm State service started.")
        super(UpdateVmState, self).start()
        self.listener.start()
        # self.listener.wait()
        # timer to have wait() work
        self.tg.add_timer(604800, lambda: None)

    def stop(self, graceful=True):
        self.listener.stop()
        self.listener.wait()
        super(UpdateVmState, self).stop(graceful=graceful)
        LOG.info("Update Vm State service stopped")
