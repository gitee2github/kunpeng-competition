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
from hostha.api.v1.schemas.configuration import CONFIGURATION_SCHEMA
from hostha.api.wsgi import validation as v
from hostha.api.wsgi import acl
from hostha.db import api as db_api
from hostha.common.utils import api as u

CONF = cfg.CONF
LOG = log.getLogger(__name__)
rest = u.RestV2("configuration", __name__)


@rest.get("/configuration")
@acl.enforce("hostha:configuration:get")
def configuration_get(data):
    ctx = context.ctx()
    configurations = db_api.configuration_list(ctx)
    conf_list = [dict(config) for config in configurations]
    conf_json = {"configurations": conf_list}
    return u.render(conf_json)


@rest.patch("/configuration")
@acl.enforce("hostha:configuration:update")
@v.validate(CONFIGURATION_SCHEMA)
def ha_config_update(data):
    ctx = context.ctx()
    if data["group"] and data["name"]:
        filters = {"group": data["group"],
                   "name": data["name"]}
        id = db_api.configuration_get_by_name(ctx, filters)["id"]
        values = {"value": data["value"]}
        db_api.configuration_update(ctx, id, values)

    return u.render()
