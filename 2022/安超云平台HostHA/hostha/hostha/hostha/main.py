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

from hostha import config
from hostha.hostha import update_vm_state as uvs
from hostha.hostha import check_host_by_consul
from hostha.common.utils import patches

patches.eventlet_monkey_patch()
compute_ha = cfg.OptGroup(name='compute_ha',
                          title='HA for compute, include hosts and VMs.')

compute_ha_opts = [

    cfg.IntOpt("host_check_interval",
               default=10,
               help="The interval to check host health."),
    cfg.IntOpt("host_check_retry",
               default=3,
               help="The times of host health check to confirm health "
                    "changes."),
]

CONF = cfg.CONF
CONF.register_group(compute_ha)
CONF.register_opts(compute_ha_opts, group=compute_ha)

LOG = log.getLogger(__name__)


def main():
    config.setup_config()
    LOG.info("Hostha Service started")

    checkhost = check_host_by_consul.HostCheckManager()
    updatevmstate = uvs.UpdateVmState()

    launcher = service.ProcessLauncher(CONF)
    launcher.launch_service(checkhost)
    launcher.launch_service(updatevmstate)
    launcher.wait()
