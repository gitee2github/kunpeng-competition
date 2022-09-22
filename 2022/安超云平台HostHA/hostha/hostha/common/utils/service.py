
import abc
import six
import socket

from oslo_config import cfg
from oslo_log import log
import oslo_messaging as om
from oslo_service import service


CONF = cfg.CONF
LOG = log.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class ServiceManager(object):

    @abc.abstractproperty
    def service_name(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def api_version(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def publisher_id(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def conductor_topic(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def notification_topics(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def conductor_endpoints(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def notification_endpoints(self):
        raise NotImplementedError()

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2012 eNovance


class Service(service.ServiceBase):

    API_VERSION = '1.0'

    def __init__(self, manager_class):
        super(Service, self).__init__()
        self.manager = manager_class()

        self.publisher_id = self.manager.publisher_id
        self.api_version = self.manager.api_version

        self.conductor_topic = self.manager.conductor_topic
        self.notification_topics = self.manager.notification_topics

        self.conductor_fanout = False

        self.heartbeat = None

        self.service_name = self.manager.service_name

        self.conductor_endpoints = [
            ep(self) for ep in self.manager.conductor_endpoints
        ]
        self.notification_endpoints = self.manager.notification_endpoints

        self._transport = None
        self._notification_transport = None
        self._conductor_client = None

        self.conductor_topic_handler = None
        self.notification_handler = None

        if self.manager.conductor_fanout:
            self.conductor_fanout = True

        if self.conductor_topic and self.conductor_endpoints:
            self.conductor_topic_handler = self.build_topic_handler(
                self.conductor_topic, self.conductor_endpoints)

    @property
    def transport(self):
        if self._transport is None:
            self._transport = om.get_transport(CONF)
        return self._transport

    @property
    def notification_transport(self):
        if self._notification_transport is None:
            self._notification_transport = om.get_notification_transport(CONF)
        return self._notification_transport

    @property
    def conductor_client(self):
        if self._conductor_client is None:
            target = om.Target(
                topic=self.conductor_topic,
                version=self.API_VERSION,
                fanout=self.conductor_fanout,
            )
            self._conductor_client = om.RPCClient(
                self.transport, target)
        return self._conductor_client

    @conductor_client.setter
    def conductor_client(self, c):
        self.conductor_client = c

    def build_topic_handler(self, topic_name, endpoints=()):
        target = om.Target(
            topic=topic_name,
            # For compatibility, we can override it with 'host' opt
            server=socket.gethostname(),
            version=self.api_version,
        )
        return om.get_rpc_server(
            self.transport, target, endpoints,
            executor='eventlet')

    def start(self):
        LOG.debug("Connecting to '%s' (%s)",
                  CONF.transport_url, CONF.rpc_backend)
        if self.conductor_topic_handler:
            self.conductor_topic_handler.start()
        if self.notification_handler:
            self.notification_handler.start()

    def stop(self):
        LOG.debug("Disconnecting from '%s' (%s)",
                  CONF.transport_url, CONF.rpc_backend)
        if self.conductor_topic_handler:
            self.conductor_topic_handler.stop()
        if self.notification_handler:
            self.notification_handler.stop()

    def reset(self):
        """Reset a service in case it received a SIGHUP."""

    def wait(self):
        """Wait for service to complete."""

    def check_api_version(self, ctx):
        api_manager_version = self.conductor_client.call(
            ctx, 'check_api_version', api_version=self.api_version)
        return api_manager_version


def launch(conf, service_, workers=1):
    return service.launch(conf, service_, workers)
