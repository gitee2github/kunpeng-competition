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


from oslo_config import cfg
from oslo_db import api as db_api
from oslo_log import log

from hostha.common.utils import types

LOG = log.getLogger(__name__)
_BACKEND_MAPPING = {'sqlalchemy': 'hostha.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING)


def get_instance():
    """Return a DB API instance."""
    return IMPL


def setup_db():
    """Set up database, create tables, etc.

    Return True on success, False otherwise
    """
    return IMPL.setup_db()


def drop_db():
    """Drop database.

    Return True on success, False otherwise
    """
    return IMPL.drop_db()


def get_session():
    return IMPL.get_session()


# Helpers for building constraints / equality checks


def constraint(**conditions):
    """Return a constraint object suitable for use with some updates."""
    return IMPL.constraint(**conditions)


def equal_any(*values):
    """Return an equality condition object suitable for use in a constraint.

    Equal_any conditions require that a model object's attribute equal any
    one of the given values.
    """
    return IMPL.equal_any(*values)


def not_equal(*values):
    """Return an inequality condition object suitable for use in a constraint.

    Not_equal conditions require that a model object's attribute differs from
    all of the given values.
    """
    return IMPL.not_equal(*values)


def strip_integer_id(resource):
    # if "id" in resource and type(resource["id"]) is int:
    #    del resource["id"]
    return resource


def to_dict(func):

    def decorator(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, types.Page):
            resources = [strip_integer_id(item.to_dict()) for item in res]
            return types.Page(resources, res.prev, res.next)
        if isinstance(res, list):
            return [strip_integer_id(item.to_dict()) for item in res]
        if res:
            return strip_integer_id(res.to_dict())
        else:
            return None

    return decorator


def to_dict_total(func):

    def decorator(*args, **kwargs):
        res, total_count = func(*args, **kwargs)
        if isinstance(res, types.Page):
            resources = [strip_integer_id(item.to_dict()) for item in res]
            return types.Page(resources, res.prev, res.next), total_count
        if isinstance(res, list):
            return [strip_integer_id(item.to_dict()) for item in res],\
                   total_count
        if res:
            return strip_integer_id(res.to_dict()), total_count
        else:
            return None, None

    return decorator


@to_dict
def ha_config_get(ctx):
    return IMPL.ha_config_get(ctx)


def ha_config_update(ctx, data):
    return IMPL.ha_config_update(ctx, data)

# # HOST AND VM HA # #
# ## ha_configuration ## #


def configuration_list(ctx):
    return IMPL.configuration_list(ctx)


def configuration_get_by_name(ctx, filters):
    return IMPL.configuration_get_by_filters(ctx, filters)


def configuration_update(ctx, id, values):
    return IMPL.configuration_update(ctx, id, values)


# ## ha_host ## #
def ha_host_get_by_filters(ctx, filters):
    return IMPL.ha_host_get_by_filters(ctx, filters)


def ha_host_update(ctx, id, values):
    return IMPL.ha_host_update(ctx, id, values)


def ha_host_get_by_id(ctx, id):
    return IMPL.ha_host_get_by_id(ctx, id)


def ha_host_delete(ctx, id):
    return IMPL.ha_host_delete(ctx, id)


def ha_host_create(ctx, values):
    return IMPL.ha_host_create(ctx, values)


# ## ha_host_evacuation ## #
def ha_host_evacuation_get_by_filters(ctx, filters):
    return IMPL.ha_host_evacuation_get_by_filters(ctx, filters)


def ha_host_evacuation_update(ctx, id, values):
    return IMPL.ha_host_evacuation_update(ctx, id, values)


def ha_host_evacuation_get_by_id(ctx, id):
    return IMPL.ha_host_evacuation_get_by_id(ctx, id)


def ha_host_evacuation_delete(ctx, id):
    return IMPL.ha_host_evacuation_delete(ctx, id)


def ha_host_evacuation_create(ctx, values):
    return IMPL.ha_host_evacuation_create(ctx, values)


# ## host_vm_evacuation ## #
def host_vm_evacuation_get_by_filters(ctx, filters):
    return IMPL.host_vm_evacuation_get_by_filters(ctx, filters)


def host_vm_evacuation_update(ctx, id, values):
    return IMPL.host_vm_evacuation_update(ctx, id, values)


def host_vm_evacuation_get_by_id(ctx, id):
    return IMPL.host_vm_evacuation_get_by_id(ctx, id)


def host_vm_evacuation_delete(ctx, id):
    return IMPL.host_vm_evacuation_delete(ctx, id)


def host_vm_evacuation_create(ctx, values):
    return IMPL.host_vm_evacuation_create(ctx, values)


# ## host_vm_recovery ## #
def host_vm_recovery_get_by_filters(ctx, filters):
    return IMPL.host_vm_recovery_get_by_filters(ctx, filters)


def host_vm_recovery_update(ctx, id, values):
    return IMPL.host_vm_recovery_update(ctx, id, values)


def host_vm_recovery_get_by_id(ctx, id):
    return IMPL.host_vm_recovery_get_by_id(ctx, id)


def host_vm_recovery_delete(ctx, id):
    return IMPL.host_vm_recovery_delete(ctx, id)


def host_vm_recovery_create(ctx, values):
    return IMPL.host_vm_recovery_create(ctx, values)
