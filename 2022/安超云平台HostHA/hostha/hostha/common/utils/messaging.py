# Copyright 2013 eNovance <licensing@enovance.com>
#
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

import oslo_messaging
from oslo_messaging import serializer as oslo_serializer


_SERIALIZER = oslo_serializer.JsonPayloadSerializer()


def setup():
    oslo_messaging.set_transport_defaults('hostha')


def get_transport(conf, url=None):
    transport = oslo_messaging.get_transport(conf, url=url)
    return transport


def get_rpc_server(conf, transport, topic, endpoint):
    """Return a configured oslo_messaging rpc server."""
    target = oslo_messaging.Target(server=conf.host, topic=topic)
    server = oslo_messaging.get_rpc_server(
            transport, target, [endpoint],
            executor='eventlet',
            serializer=_SERIALIZER)
    return server


def get_rpc_client(transport, retry=None, **kwargs):
    """Return a configured oslo_messaging RPCClient."""
    target = oslo_messaging.Target(**kwargs)
    client = oslo_messaging.RPCClient(
            transport, target,
            serializer=_SERIALIZER,
            retry=retry)
    return client


def get_notification_listener(transport, topic, endpoint,
                              allow_requeue=False):
    target = oslo_messaging.Target(topic=topic)
    listener = oslo_messaging.get_notification_listener(
        transport, [target], [endpoint],
        executor='eventlet',
        allow_requeue=allow_requeue)
    return listener


def get_notifier(transport, publisher_id, topic):
    """Return a configured oslo_messaging notifier."""
    notifier = oslo_messaging.Notifier(
        transport,
        publisher_id=publisher_id,
        driver="messagingv2",
        topic=topic)
    return notifier
