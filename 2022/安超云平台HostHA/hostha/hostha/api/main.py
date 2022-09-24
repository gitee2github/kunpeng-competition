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
from oslo_log import log
from oslo_service import service
from oslo_service import wsgi
from oslo_service import sslutils
from hostha import config
from hostha.common.utils import policy
from hostha.version import PROJECT_NAME

from hostha.common.utils import patches
patches.eventlet_monkey_patch()
CONF = cfg.CONF
LOG = log.getLogger(__name__)


class CloudultraService(wsgi.Server):

    def __init__(self, service_name, app):
        super(CloudultraService, self).__init__(
            CONF, service_name, app,
            host=CONF.host,
            port=CONF.port,
            use_ssl=sslutils.is_enabled(CONF))

    def start(self):
        super(CloudultraService, self).start()


def main():
    config.set_cors_middleware_defaults()
    config.setup_config()
    LOG.info("OpenStack CloudUltra service started")

    policy.setup_policy()
    launcher = service.ProcessLauncher(CONF, wait_interval=0.1)
    app_loader = wsgi.Loader(CONF)

    app = app_loader.load_app(PROJECT_NAME)
    api_service = CloudultraService(PROJECT_NAME, app)
    launcher.launch_service(api_service)

    launcher.wait()
