# Copyright (c) 2016 ChinaC Inc.

import datetime

from oslo_config import cfg
from oslo_serialization import jsonutils
import six

from hostha import exceptions
from hostha.i18n import _

CONF = cfg.CONF

# SPDX-License-Identifier: Apache-2.0
# Copyright 2011 OpenStack LLC.


class ActionDispatcher(object):
    """Maps method name to local methods through action name."""

    def dispatch(self, *args, **kwargs):
        """Find and call local method."""
        action = kwargs.pop('action', 'default')
        action_method = getattr(self, str(action), self.default)
        return action_method(*args, **kwargs)

    def default(self, data):
        raise NotImplementedError()


class DictSerializer(ActionDispatcher):
    """Default request body serialization."""

    def serialize(self, data, action='default'):
        return self.dispatch(data, action=action)

    def default(self, data):
        return ""


class JSONDictSerializer(DictSerializer):
    """Default JSON request body serialization."""

    def default(self, data):
        def sanitizer(obj):
            if isinstance(obj, datetime.datetime):
                _dtime = obj - datetime.timedelta(microseconds=obj.microsecond)
                return _dtime.isoformat()
            return six.text_type(obj)
        return jsonutils.dumps(data, default=sanitizer)


class TextDeserializer(ActionDispatcher):
    """Default request body deserialization."""

    def deserialize(self, datastring, action='default'):
        return self.dispatch(datastring, action=action)

    def default(self, datastring):
        return {}


class JSONDeserializer(TextDeserializer):

    def _from_json(self, datastring):
        try:
            return jsonutils.loads(datastring)
        except ValueError:
            msg = _("cannot understand JSON")
            raise exceptions.MalformedRequestBody(msg)

    def default(self, datastring):
        return {'body': self._from_json(datastring)}
