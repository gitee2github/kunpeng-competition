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

from oslo_log import log
from oslo_config import cfg

from hostha import context
from hostha.api.v1.schemas.host_ha import HOST_HA_SCHEMA
from hostha.api.wsgi import validation as v
from hostha.api.wsgi import acl
from hostha.db import api as db_api
from hostha.common.utils import api as u

CONF = cfg.CONF
LOG = log.getLogger(__name__)
rest = u.RestV2("host_ha", __name__)


@rest.get("/host_ha")
@acl.enforce("hostha:host_ha:get")
def configuration_get(data):
    ctx = context.ctx()
    hosts = db_api.ha_host_get_by_filters(ctx, filters={})
    hosts_list = [dict(host) for host in hosts]
    hosts_json = {"hosts": hosts_list}
    return u.render(hosts_json)


@rest.patch("/host_ha")
@acl.enforce("hostha:host_ha:update")
@v.validate(HOST_HA_SCHEMA)
def ha_config_update(data):
    ctx = context.ctx()
    key_list = ["host_ha_enabled", "vm_ha_enabled", "mgmt_ip",
                "ipmi_ip", "ipmi_user", "ipmi_password",
                "store_ip"]
    if data["hostname"]:
        filters = {"hostname": data["hostname"]}
        id = db_api.ha_host_get_by_filters(ctx, filters)[0]["id"]
        values = {}
        for key in data.keys():
            if key in key_list:
                values[key] = data[key]
        if values:
            LOG.debug("update host_ha %s", values)
            db_api.ha_host_update(ctx, id, values)
    return u.render()

@rest.post("/host_ha")
@acl.enforce("hostha:host_ha:create")
@v.validate(HOST_HA_SCHEMA)
def host_ha_create(data):
    ctx = context.ctx()
    filter = {'hostname': data.get('hostname')}
    LOG.info('get data %s' % data)
    update_hosts = db_api.ha_host_get_by_filters(ctx, filter)
    if update_hosts:
        host = update_hosts[0]
        db_api.ha_host_update(ctx, host['id'], data)
        LOG.info("update host hostname:%s id:%s success ",
                 data['hostname'], host['id'])
    else:
        data = db_api.ha_host_create(ctx, data)
        LOG.info("init host hostname:%s id:%s success ",
                 data['hostname'], data['id'])

    return u.render()


@rest.delete("/host_ha/<hostname>")
@acl.enforce("hostha:host_ha:delete")
def host_ha_delete(hostname):
    ctx = context.ctx()
    filter = {'hostname': hostname}
    LOG.info('going to del host with name %s' % hostname)
    del_hosts = db_api.ha_host_get_by_filters(ctx, filter)
    if del_hosts:
        host = del_hosts[0]
        db_api.ha_host_delete(ctx, host["id"])
        LOG.info("success del host")
    else:
        raise NotFoundError('host with name %s not found' % hostname)
    return u.render()
