# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import time

from oslo_log import log

from hostha.common.openstack import clients

LOG = log.getLogger(__name__)


class NovaHelper(object):

    def __init__(self, osc=None):
        """:param osc: an OpenStackClients instance"""
        self.osc = osc if osc else clients.OpenStackClients()
        self.nova = self.osc.nova()

    def list_instances(self):
        return self.nova.servers.list(search_opts={'all_tenants': True})

    def get_instance(self, instance_id):
        return self.nova.servers.get(instance_id)

    def delete_instance(self, instance_id):
        return self.nova.servers.delete(instance_id)

    def create_instance(self, **kwargs):
        """This method stops a given instance.

        :param: name, image, flavor,
        :kwargs: meta=None, files=None,
                 reservation_id=None, min_count=None,
                 max_count=None, security_groups=None, userdata=None,
                 key_name=None, availability_zone=None,
                 block_device_mapping=None, block_device_mapping_v2=None,
                 nics=None, scheduler_hints=None,
                 config_drive=None, disk_config=None, admin_pass=None,
                 access_ip_v4=None, access_ip_v6=None, **kwargs.
        """
        return self.nova.servers.create(**kwargs)

    def wait_for_instance_schedule(self, server, retry, sleep):
        """Waits for server to be scheduled to one compute node

        :param server: server object.
        :param retry: how many times to retry
        :param sleep: seconds to sleep between the retries
        """
        while getattr(server, 'OS-EXT-SRV-ATTR:host') is None and retry:
            time.sleep(sleep)
            server = self.nova.servers.get(server)
            retry -= 1
        if not retry:
            return False
        return True

    def wait_for_instance_state(self, server, state, retry, sleep):
        """Waits for server to be in a specific state

        The state can be one of the following :
        active, stopped

        :param server: server object.
        :param state: for which state we are waiting for
        :param retry: how many times to retry
        :param sleep: seconds to sleep between the retries
        """
        while getattr(server, 'OS-EXT-STS:vm_state') != state and retry:
            time.sleep(sleep)
            server = self.nova.servers.get(server)
            retry -= 1
        return getattr(server, 'OS-EXT-STS:vm_state') == state

    def stop_instance(self, instance_id):
        """This method stops a given instance.

        :param instance_id: the unique id of the instance to stop.
        """
        LOG.debug("Trying to stop instance %s ..." % instance_id)

        instance = self.get_instance(instance_id)

        if not instance:
            LOG.debug("Instance not found: %s" % instance_id)
            return False
        elif getattr(instance, 'OS-EXT-STS:vm_state') == "stopped":
            LOG.debug("Instance has been stopped: %s" % instance_id)
            return True
        else:
            self.nova.servers.stop(instance_id)

            if self.wait_for_instance_state(instance, "stopped", 5, 30):
                LOG.debug("Instance %s stopped." % instance_id)
                return True
            else:
                return False

    def list_flavors(self):
        return self.nova.flavors.list()
