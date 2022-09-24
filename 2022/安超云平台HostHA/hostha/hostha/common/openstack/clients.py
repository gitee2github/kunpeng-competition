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

from glanceclient import client as glclient
from keystoneauth1 import loading as ka_loading
from keystoneclient import client as keyclient
from neutronclient.neutron import client as netclient
from novaclient import client as nvclient

from hostha import exceptions

from hostha import conf

CONF = conf.CONF

_CLIENTS_AUTH_GROUP = 'cloudultra_clients_auth'


class OpenStackClients(object):
    """Convenience class to create and cache client instances."""

    def __init__(self):
        self.reset_clients()

    def reset_clients(self):
        self._session = None
        self._keystone = None
        self._nova = None
        self._glance = None
        self._neutron = None

    def _get_keystone_session(self):
        auth = ka_loading.load_auth_from_conf_options(CONF,
                                                      _CLIENTS_AUTH_GROUP)
        sess = ka_loading.load_session_from_conf_options(CONF,
                                                         _CLIENTS_AUTH_GROUP,
                                                         auth=auth)
        return sess

    @property
    def auth_url(self):
        return self.keystone().auth_url

    @property
    def session(self):
        if not self._session:
            self._session = self._get_keystone_session()
        return self._session

    @exceptions.wrap_keystone_exception
    def keystone(self):
        if not self._keystone:
            self._keystone = keyclient.Client(session=self.session)

        return self._keystone

    @exceptions.wrap_keystone_exception
    def glance(self):
        if self._glance:
            return self._glance

        self._glance = glclient.Client('2',
                                       session=self.session)
        return self._glance

    @exceptions.wrap_keystone_exception
    def nova(self):
        if self._nova:
            return self._nova

        self._nova = nvclient.Client('2',
                                     session=self.session)
        return self._nova

    @exceptions.wrap_keystone_exception
    def neutron(self):
        if self._neutron:
            return self._neutron

        self._neutron = netclient.Client('2.0',
                                         session=self.session)
        self._neutron.format = 'json'
        return self._neutron
