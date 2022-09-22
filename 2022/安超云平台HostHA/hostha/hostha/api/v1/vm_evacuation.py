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
from oslo_log import log
from oslo_config import cfg

from hostha import context
from hostha.api.v1.schemas.vm_evacuation import VM_EVACUATION_SCHEMA
from hostha.api.wsgi import validation as v
from hostha.api.wsgi import acl
from hostha.db import api as db_api
from hostha.common.utils import api as u

CONF = cfg.CONF
LOG = log.getLogger(__name__)
rest = u.RestV2("vm_evacuation", __name__)


@rest.get("/vm_evacuation")
@acl.enforce("hostha:vm_evacuation:get")
@v.validate(VM_EVACUATION_SCHEMA)
def vm_evacuation_get(data):
    ctx = context.ctx()
    filters = {}
    if 'host_evacuation' in data:
        filters['host_op_id'] = data['host_evacuation']
    if 'source_host' in data:
        filters['src_host'] = data['source_host']
    if 'result' in data:
        filters['result'] = data['result']
    if 'start_time' in data:
        filters['started_at__gt'] = datetime.strptime(data['start_time'],
                                                      "%Y-%m-%d %H:%M:%S")
    if 'end_time' in data:
        filters['started_at__lt'] = datetime.strptime(data['end_time'],
                                                      "%Y-%m-%d %H:%M:%S")
    for key in ['marker', 'limit', 'sort_key', 'sort_dir']:
        if data.get(key) is not None:
            filters[key] = data[key]

    records = db_api.host_vm_evacuation_get_by_filters(ctx, filters)
    record_list = [dict(record) for record in records]
    conf_json = {"records": record_list}
    return u.render(conf_json)
