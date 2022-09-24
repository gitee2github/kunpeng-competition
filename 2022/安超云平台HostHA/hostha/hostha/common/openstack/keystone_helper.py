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

from oslo_log import log

from hostha.common.openstack import clients

LOG = log.getLogger(__name__)


class KeystoneHelper(object):

    def __init__(self, osc=None):
        """:param osc: an OpenStackClients instance"""
        self.osc = osc if osc else clients.OpenStackClients()
        self.keystone = self.osc.keystone()

    def list_projects(self):
        return self.keystone.projects.list()

    def get_project_by_name(self, project_name):
        all_projects = self.list_projects()
        for project in all_projects:
            if project.name == project_name:
                return project
        return None

    def list_endpoints(self):
        return self.keystone.endpoints.list()

    def list_services(self):
        return self.keystone.services.list()
