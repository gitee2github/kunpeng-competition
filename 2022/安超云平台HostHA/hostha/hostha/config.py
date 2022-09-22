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


import oslo_i18n
from oslo_cache import core as cache
from oslo_config import cfg
from oslo_log import log
from oslo_middleware import cors
from oslo_db import options

from . import version
from .version import PROJECT_NAME

cli_opts = [
    cfg.StrOpt('host', default='127.0.0.1',
               help='Hostname or IP address that will be used to listen on.'),
    cfg.PortOpt('port', default=12306,
                help='Port that will be used to listen on.'),
    cfg.BoolOpt('log-exchange', default=False,
                help='Log request/response exchange details: environ, '
                     'headers and bodies.'),
    cfg.IntOpt('api_workers', default=1,
               help="Number of workers for Sahara API service (0 means "
                    "all-in-one-thread configuration)."),
    cfg.StrOpt('domain_name', default="default",
               help="Domain of hostha service in Keystone"),
    # cfg.StrOpt('tenant_name',
    #            default="service",
    #            help="Tenant name of hostha service in Keystone"),
    cfg.StrOpt('username',
               default="hostha",
               help="User name of hostha service in Keystone"),
    cfg.StrOpt('password',
               help="Password of hostha service in Keystone"),
    cfg.StrOpt('region',
               default=None,
               help="Region name")
]


CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)
LOG = log.getLogger(__name__)
DEFAULT_LOG_LEVELS = [
    'amqplib=WARN',
    'qpid.messaging=INFO',
    'stevedore=INFO',
    'eventlet.wsgi.server=WARN',
    'sqlalchemy=WARN',
    'boto=WARN',
    'suds=INFO',
    'keystone=INFO',
    'paramiko=WARN',
    'requests=WARN',
    'iso8601=WARN',
    'oslo_messaging=INFO',
    'neutronclient=INFO',
]
LOG_CONTEXT_FORMAT = ("%(asctime)s.%(msecs)03d %(process)d %(levelname)s "
                      "%(name)s [%(request_id)s] %(instance)s%(message)s")


def set_cors_middleware_defaults():
    """Update default configuration options for oslo.middleware."""
    # CORS Defaults
    cfg.set_defaults(cors.CORS_OPTS,
                     allow_headers=['X-Auth-Token',
                                    'X-Identity-Status',
                                    'X-Roles',
                                    'X-Service-Catalog',
                                    'X-User-Id',
                                    'X-Tenant-Id',
                                    'X-OpenStack-Request-ID'],
                     expose_headers=['X-Auth-Token',
                                     'X-Subject-Token',
                                     'X-Service-Token',
                                     'X-OpenStack-Request-ID'],
                     allow_methods=['GET',
                                    'PUT',
                                    'POST',
                                    'DELETE',
                                    'PATCH']
                     )


def setup_config(argv=None, config_files=None):
    oslo_i18n.enable_lazy()
    log.register_options(CONF)
    log.set_defaults(logging_context_format_string=LOG_CONTEXT_FORMAT,
                     default_log_levels=DEFAULT_LOG_LEVELS)
    options.set_defaults(CONF)
    cache.configure(CONF)
    CONF(argv,
         project=version.PROJECT_NAME,
         version=version.version_info.version_string(),
         default_config_files=config_files)

    log.setup(CONF, PROJECT_NAME)
