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


import itertools
import sys
import threading
import datetime
import operator
import sqlalchemy.orm.exc
from sqlalchemy import inspect
from sqlalchemy.orm import exc


from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils
from oslo_db import exception
from oslo_utils import timeutils
from oslo_log import log as logging

from hostha.db.sqlalchemy import models as m
from hostha import exceptions as ex
from hostha.common.utils import types
from hostha import constants


LOG = logging.getLogger(__name__)

CONF = cfg.CONF

_FACADE = None
_LOCK = threading.Lock()

_VALID_SORT_DIR = [
    "-".join(x) for x in itertools.product(["asc", "desc"],
                                           ["nullsfirst", "nullslast"])]

_VALID_OPERATORS = {
    "": operator.eq,
    "eq": operator.eq,
    "neq": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "in": lambda field, choices: field.in_(choices),
    "notin": lambda field, choices: field.notin_(choices),
}


def _create_facade_lazily():
    global _LOCK, _FACADE

    if _FACADE is None:
        with _LOCK:
            if _FACADE is None:
                _FACADE = db_session.EngineFacade.from_config(CONF,
                                                              sqlite_fk=True)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """
    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def _get_prev_and_next_objects(objects, limit, marker, order=None,
                               position=None):
    if order == constants.ORDER_DESC:
        objects.reverse()
    position = position
    if marker:
        for pos, obj in enumerate(objects):
            if obj.id == marker.id:
                position = pos
                break
        if position - limit >= 0:
            prev_marker = objects[position - limit].id
        else:
            prev_marker = None
        if position + limit < len(objects):
            next_marker = objects[position + limit].id
        else:
            next_marker = None
    elif position and position != 0:
        if position - limit >= 0:
            prev_marker = objects[position - limit].id
        else:
            prev_marker = None
        if position + limit < len(objects):
            next_marker = objects[position + limit].id
        else:
            next_marker = None

        for pos, obj in enumerate(objects):
            if (position - 1) == pos:
                marker = obj
                break
    else:
        if limit < len(objects):
            next_marker = objects[limit - 1].id
        else:
            next_marker = None
        prev_marker = None

    total_count = len(objects)
    return prev_marker, next_marker, marker, total_count


def _populate_tenant_id_for_creation(ctx, data):
    # Admin user can create resource for other tenant
    if ctx is not None:
        if "tenant_id" in data:
            if not ctx.is_admin:
                msg = "You are not authorized to use tenant_id parameter"
                raise ex.Forbidden(message=msg)
        else:
            data["tenant_id"] = ctx.tenant_id


def _apply_sorting_filter(ctx, model, query, sort_keys, sort_dirs):
    for current_sort_key, current_sort_dir in zip(sort_keys, sort_dirs):
        try:
            inspect(model).all_orm_descriptors[current_sort_key]
        except KeyError:
            raise exception.InvalidSortKey(current_sort_key)
        else:
            sort_key_attr = getattr(model, current_sort_key)

        try:
            main_sort_dir, __, null_sort_dir = current_sort_dir.partition("-")
            sort_dir_func = {
                'asc': sqlalchemy.asc,
                'desc': sqlalchemy.desc,
            }[main_sort_dir]

            null_order_by_stmt = {
                "": None,
                "nullsfirst": sort_key_attr.is_(None),
                "nullslast": sort_key_attr.isnot(None),
            }[null_sort_dir]
        except KeyError:
            raise ValueError("Unknown sort direction, "
                             "must be one of: %s" %
                             ", ".join(_VALID_SORT_DIR))

        if null_order_by_stmt is not None:
            query = query.order_by(sqlalchemy.desc(null_order_by_stmt))
        query = query.order_by(sort_dir_func(sort_key_attr))
    return query


def _apply_tenant_id_filter(ctx, query):
    # Admin user can access all tenants
    # Unprivileged user can only access his own tenant
    if ctx is not None:
        if not ctx.is_admin:
            query = query.filter_by(tenant_id=ctx.tenant_id)
    return query


def __decompose_filter(raw_fieldname):
    """Decompose a filter name into its 2 subparts

    A filter can take 2 forms:

    - "<FIELDNAME>" which is a syntactic sugar for "<FIELDNAME>__eq"
    - "<FIELDNAME>__<OPERATOR>" where <OPERATOR> is the comparison operator
      to be used.
    """
    separator = '__'
    fieldname, separator, operator_ = raw_fieldname.partition(separator)

    if operator_ and operator_ not in _VALID_OPERATORS:
        raise exception.InvalidOperator(
            operator=operator_, valid_operators=_VALID_OPERATORS)

    return fieldname, operator_


def __add_simple_filter(query, model, fieldname, value, operator_):
    field = getattr(model, fieldname)

    if (fieldname != 'deleted' and value and
            field.type.python_type is datetime.datetime):
        if not isinstance(value, datetime.datetime):
            value = timeutils.parse_isotime(value)

    return query.filter(_VALID_OPERATORS[operator_](field, value))


def _add_filters(query, model, filters=None, fields=[]):
    """Generic way to add filters to a CloudUltra model

    Each filter key provided by the `filters` parameter will be decomposed
    into 2 pieces: the field name and the comparison operator

    - "": By default, the "eq" is applied if no operator is provided
    - "eq", which stands for "equal" : e.g. {"state__eq": "PENDING"}
      will result in the "WHERE state = 'PENDING'" clause.
    - "neq", which stands for "not equal" : e.g. {"state__neq": "PENDING"}
      will result in the "WHERE state != 'PENDING'" clause.
    - "gt", which stands for "greater than" : e.g.
      {"created_at__gt": "2016-06-06T10:33:22.063176"} will result in the
      "WHERE created_at > '2016-06-06T10:33:22.063176'" clause.
    - "gte", which stands for "greater than or equal to" : e.g.
      {"created_at__gte": "2016-06-06T10:33:22.063176"} will result in the
      "WHERE created_at >= '2016-06-06T10:33:22.063176'" clause.
    - "lt", which stands for "less than" : e.g.
      {"created_at__lt": "2016-06-06T10:33:22.063176"} will result in the
      "WHERE created_at < '2016-06-06T10:33:22.063176'" clause.
    - "lte", which stands for "less than or equal to" : e.g.
      {"created_at__lte": "2016-06-06T10:33:22.063176"} will result in the
      "WHERE created_at <= '2016-06-06T10:33:22.063176'" clause.
    - "in": e.g. {"state__in": ('SUCCEEDED', 'FAILED')} will result in the
      "WHERE state IN ('SUCCEEDED', 'FAILED')" clause.

    :param query: a :py:class:`sqlalchemy.orm.query.Query` instance
    :param model: the model class the filters should relate to
    :param filters: dict with the following structure {"fieldname": value}
    :param plain_fields: a :py:class:`sqlalchemy.orm.query.Query` instance
    """
    timestamp_mixin_fields = ['created_at', 'updated_at', 'finished_at']
    filters = filters or {}

    fields = tuple((list(fields) or []) + timestamp_mixin_fields)

    for raw_fieldname, value in filters.items():
        fieldname, operator_ = __decompose_filter(raw_fieldname)
        if fieldname in fields:
            query = __add_simple_filter(
                query, model, fieldname, value, operator_)

    return query


def _add_host_evacuation_filters(query, filters):
    if filters is None:
        filters = {}

    fields = ['id', 'hostname', 'started_at']

    query = _add_filters(
        query=query, model=m.HAHostEvacuation, filters=filters, fields=fields)

    return query


def _add_vm_evacuation_filters(query, filters):
    if filters is None:
        filters = {}

    fields = ['id', 'src_host', 'des_host', 'started_at', 'result',
              'host_op_id']

    query = _add_filters(
        query=query, model=m.HostVmEvacuation, filters=filters, fields=fields)

    return query


def alarm_get(ctx, alarm_id):
    query = ctx.session.query(m.Alarm)
    query = query.filter_by(id=alarm_id)
    query = _apply_tenant_id_filter(ctx, query)

    try:
        return query.one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise ex.AlarmNotFoundError(alarm_id)


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    query = utils.paginate_query(query, model, limit, sort_keys,
                                 marker=marker, sort_dir=sort_dir)
    return query.all()


def _pagination_query(ctx, model, marker, limit, sort_order, sort_keys,
                      filters=None):
    if 'id' not in sort_keys:
        sort_keys.append('id')

    query = ctx.session.query(model)
    query = _apply_tenant_id_filter(ctx, query)
    if filters:
        query = query.filter_by(**filters)
    prev_marker, next_marker, marker, total_count = _get_prev_and_next_objects(
        query.order_by(*sort_keys).all(),
        limit,
        marker,
        order=sort_order)
    resources = utils.paginate_query(query,
                                     model,
                                     limit,
                                     sort_keys,
                                     marker=marker,
                                     sort_dir=sort_order)
    return types.Page(resources, prev_marker, next_marker)


def _multi_key_pagination_query(ctx, model, marker, limit, sort,
                                filters=None, offset=None):
    sort_keys = [x['key'] for x in sort]
    sort_dirs = [x['order'] for x in sort]
    if 'id' not in sort_keys:
        sort_keys.append('id')
        sort_dirs.append('asc')

    query = ctx.session.query(model)
    query = _apply_tenant_id_filter(ctx, query)
    if filters:
        if 'start_time' in filters and 'end_time' in filters:
            start_time = datetime.datetime.strptime(filters['start_time'],
                                                    "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.datetime.strptime(filters['end_time'],
                                                  "%Y-%m-%dT%H:%M:%S")
            del filters['start_time']
            del filters['end_time']
            query = query.filter(model.created_at >= start_time)
            query = query.filter(model.created_at <= end_time)
        query = query.filter_by(**filters)
    prev_marker, next_marker, marker, total_count = _get_prev_and_next_objects(
        _apply_sorting_filter(ctx, model, query, sort_keys, sort_dirs).all(),
        limit,
        marker,
        position=offset)
    resources = utils.paginate_query(query,
                                     model,
                                     limit,
                                     sort_keys,
                                     marker=marker,
                                     sort_dirs=sort_dirs)
    return types.Page(resources, prev_marker, next_marker), total_count


def _get_list(ctx, model, filters=None):
    query = ctx.session.query(model)
    if filters:
        query = query.filter_by(**filters)
    return query.all()


def _get(ctx, model, filters=None):
    query = ctx.session.query(model)
    if filters:
        query = query.filter_by(**filters)
    try:
        obj = query.one()
    except exc.NoResultFound:
        raise ex.ResourceNotFound(name=model.__name__, id=str(filters))
    return obj


def _update(ctx, model, id, values):
    with ctx.session.begin(subtransactions=True):
        query = ctx.session.query(model)
        query = query.filter_by(id=id)
        try:
            ref = query.with_lockmode('update').one()
        except exc.NoResultFound:
            raise ex.ResourceNotFound(name=model.__name__, id=str(id))
        ref.update(values)
        ctx.session.flush(objects=[ref])
    return ref


def _check_update(ctx, model, id, values):
    with ctx.session.begin(subtransactions=True):
        query = ctx.session.query(model)
        query = query.filter_by(id=id)
        try:
            update_task_val = values.get('task')
            ref = query.with_lockmode('update').one()
            LOG.info('task in db is %s, update to %s' % (ref.task,
                                                         update_task_val))
            if ref.task is not None and update_task_val is not None:
                if update_task_val == ref.task:
                    raise ex.AlreadyHaveValueERROR(update_task_val)
        except exc.NoResultFound:
            raise ex.ResourceNotFound(name=model.__name__, id=str(id))
        ref.update(values)
        ctx.session.flush(objects=[ref])
    return ref


def _get_relationships(model):
    return inspect(model).relationships


def _create(ctx, model, values):
    obj = model()
    cleaned_values = {k: v for k, v in values.items()
                      if k not in _get_relationships(model)}
    obj.update(cleaned_values)
    ctx.session.add(obj)
    ctx.session.flush(objects=[obj])
    return obj


def _destroy(ctx, model, id):

    session = get_session()
    with session.begin():
        query = ctx.session.query(model)
        query = query.filter_by(id=id)
        try:
            query.one()
        except exc.NoResultFound:
            raise ex.ResourceNotFound(name=model.__name__, id=str(id))
        query.delete()


class TableLock(object):

    def __init__(self, session, table):
        self.conn = session.connection()
        self.table = table

    def __enter__(self):
        sql = "LOCK TABLES {table} WRITE".format(table=self.table)
        self.conn.execute(sql)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sql = "UNLOCK TABLES"
        self.conn.execute(sql)


# # HOST AND VM HA # #
# ## ha_configuration ## #
def configuration_list(ctx):
    return _get_list(ctx, m.Configuration)


def configuration_get_by_filters(ctx, filters):
    return _get(ctx, m.Configuration, filters)


def configuration_update(ctx, id, values):
    return _update(ctx, m.Configuration, id, values)


# ## ha_host ## #
def ha_host_get_by_filters(ctx, filters):
    return _get_list(ctx, m.HAHost, filters)


def ha_host_update(ctx, id, values):
    return _check_update(ctx, m.HAHost, id, values)


def ha_host_get_by_id(ctx, id):
    filters = {"id": id}
    return _get(ctx, m.HAHost, filters)


def ha_host_delete(ctx, id):
    return _destroy(ctx, m.HAHost, id)


def ha_host_create(ctx, values):
    return _create(ctx, m.HAHost, values)


# ## ha_host_evacuation ## #
def ha_host_evacuation_get_by_filters(ctx, filters):
    limit = filters['limit'] if 'limit' in filters else None
    sort_key = filters['sort_key'] if 'sort_key' in filters else None
    sort_dir = filters['sort_dir'] if 'sort_dir' in filters else None
    if "marker" in filters:
        marker = ha_host_evacuation_get_by_id(ctx, filters["marker"])
    else:
        marker = None

    query = model_query(m.HAHostEvacuation)
    query = _add_host_evacuation_filters(query, filters)
    return _paginate_query(m.HAHostEvacuation, limit, marker,
                           sort_key, sort_dir, query)


def ha_host_evacuation_update(ctx, id, values):
    return _update(ctx, m.HAHostEvacuation, id, values)


def ha_host_evacuation_get_by_id(ctx, id):
    filters = {"id": id}
    return _get(ctx, m.HAHostEvacuation, filters)


def ha_host_evacuation_delete(ctx, id):
    return _destroy(ctx, m.HAHostEvacuation, id)


def ha_host_evacuation_create(ctx, values):
    return _create(ctx, m.HAHostEvacuation, values)


# ## host_vm_evacuation ## #
def host_vm_evacuation_get_by_filters(ctx, filters):
    limit = filters['limit'] if 'limit' in filters else None
    sort_key = filters['sort_key'] if 'sort_key' in filters else None
    sort_dir = filters['sort_dir'] if 'sort_dir' in filters else None
    if "marker" in filters:
        marker = host_vm_evacuation_get_by_id(ctx, filters["marker"])
    else:
        marker = None

    query = model_query(m.HostVmEvacuation)
    query = _add_vm_evacuation_filters(query, filters)
    return _paginate_query(m.HostVmEvacuation, limit, marker,
                           sort_key, sort_dir, query)


def host_vm_evacuation_update(ctx, id, values):
    return _update(ctx, m.HostVmEvacuation, id, values)


def host_vm_evacuation_get_by_id(ctx, id):
    filters = {"id": id}
    return _get(ctx, m.HostVmEvacuation, filters)


def host_vm_evacuation_delete(ctx, id):
    return _destroy(ctx, m.HostVmEvacuation, id)


def host_vm_evacuation_create(ctx, values):
    return _create(ctx, m.HostVmEvacuation, values)


# ## host_vm_recovery ## #
def host_vm_recovery_get_by_filters(ctx, filters):
    return _get_list(ctx, m.HostVmRecovery, filters)


def host_vm_recovery_update(ctx, id, values):
    return _update(ctx, m.HostVmRecovery, id, values)


def host_vm_recovery_get_by_id(ctx, id):
    filters = {"id": id}
    return _get(ctx, m.HostVmRecovery, filters)


def host_vm_recovery_delete(ctx, id):
    return _destroy(ctx, m.HostVmRecovery, id)


def host_vm_recovery_create(ctx, values):
    return _create(ctx, m.HostVmRecovery, values)
