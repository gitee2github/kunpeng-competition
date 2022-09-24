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


from eventlet.green import threading
from oslo_config import cfg
from oslo_context import context
from oslo_log import log as logging

from . import exceptions as ex
from .common.utils import sessions
from .common.utils import policy
from .db import api as db_api
from .i18n import _
from .i18n import _LW

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Context(context.RequestContext):
    def __init__(self,
                 user_id=None,
                 tenant_id=None,
                 auth_token=None,
                 service_catalog=None,
                 username=None,
                 password=None,
                 tenant_name=None,
                 roles=None,
                 is_admin=None,
                 resource_uuid=None,
                 request_id=None,
                 domain_name=None,
                 auth_plugin=None,
                 overwrite=True,
                 with_db_session=True,
                 **kwargs):
        if kwargs:
            LOG.warning(_LW('Arguments dropped when creating context: '
                            '{args}').format(args=kwargs))

        super(Context, self).__init__(auth_token=auth_token,
                                      user=user_id,
                                      tenant=tenant_id,
                                      is_admin=is_admin,
                                      resource_uuid=resource_uuid,
                                      request_id=request_id,
                                      roles=roles)
        self.service_catalog = service_catalog
        self.username = username
        self.password = password
        self.domain_name = domain_name
        self.tenant_name = tenant_name
        self.auth_plugin = auth_plugin
        if overwrite or not hasattr(context._request_store, 'context'):
            self.update_store()

        if self.is_admin is None:
            self.is_admin = policy.check_is_admin(self)

        if with_db_session:
            self.session = db_api.get_session()
        else:
            self.session = None
        self.schedule = None

    def clone(self):
        return Context(
            self.user_id,
            self.tenant_id,
            self.auth_token,
            self.service_catalog,
            self.username,
            self.tenant_name,
            self.roles,
            self.is_admin,
            self.resource_uuid,
            self.request_id,
            self.auth_plugin,
            overwrite=False)

    def to_dict(self):
        d = super(Context, self).to_dict()
        d.update({
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'service_catalog': self.service_catalog,
            'username': self.username,
            'tenant_name': self.tenant_name,
            'user_name': self.username,
            'project_name': self.tenant_name})
        return d

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def is_auth_capable(self):
        return (self.service_catalog and self.auth_token and self.tenant and
                self.user_id)

    # NOTE(adrienverge): The Context class uses the 'user' and 'tenant'
    # properties internally (inherited from oslo_context), but Sahara code
    # often uses 'user_id' and 'tenant_id'.
    @property
    def user_id(self):
        return self.user

    @user_id.setter
    def user_id(self, value):
        self.user = value

    @property
    def tenant_id(self):
        return self.tenant

    @tenant_id.setter
    def tenant_id(self, value):
        self.tenant = value

    def get_endpoint(self, service_type, url_type, region=None):
        for sc in self.service_catalog:
            if service_type == sc['type']:
                for endpoint in sc['endpoints']:
                    if (region == endpoint.get('region') and
                            url_type == endpoint['interface']):
                        return endpoint['url']
        raise ex.EndpointNotFound(service_type, url_type, region=region)

    def get_endpoint_this_region(self, ep_type):
        return self.get_endpoint(ep_type, 'internal', region=CONF.region)


def get_admin_context(request_id=None):
    return Context(is_admin=True, overwrite=False, request_id=request_id)


_CTX_STORE = threading.local()
_CTX_KEY = 'current_ctx'


def has_ctx():
    return hasattr(_CTX_STORE, _CTX_KEY)

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2013 Mirantis Inc.


def ctx():
    if not has_ctx():
        raise ex.IncorrectStateError(_("Context isn't available here"))
    return getattr(_CTX_STORE, _CTX_KEY)


def current():
    return ctx()


def set_ctx(new_ctx):
    if not new_ctx and has_ctx():
        delattr(_CTX_STORE, _CTX_KEY)
        if hasattr(context._request_store, 'context'):
            delattr(context._request_store, 'context')

    if new_ctx:
        setattr(_CTX_STORE, _CTX_KEY, new_ctx)
        setattr(context._request_store, 'context', new_ctx)


def get_auth_token():
    cur = current()
    if cur.auth_plugin:
        try:
            cur.auth_token = sessions.cache().token_for_auth(cur.auth_plugin)
        except Exception as e:
            LOG.warning(_LW("Cannot update token, reason: %s"), e)
    return cur.auth_token
