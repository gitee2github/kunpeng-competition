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

from oslo_serialization import jsonutils
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.ext import mutable

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2013 Mirantis Inc.


class JsonEncoded(sa.TypeDecorator):
    impl = sa.Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = jsonutils.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = jsonutils.loads(value)
        return value


class MutableList(mutable.Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain lists to MutableList."""
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)

            # this call will raise ValueError
            return mutable.Mutable.coerce(key, value)
        return value

    def __add__(self, value):
        """Detect list add events and emit change events."""
        list.__add__(self, value)
        self.changed()

    def append(self, value):
        """Detect list add events and emit change events."""
        list.append(self, value)
        self.changed()

    def __setitem__(self, key, value):
        """Detect list set events and emit change events."""
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, i):
        """Detect list del events and emit change events."""
        list.__delitem__(self, i)
        self.changed()


def JsonDictType():
    """Returns an SQLAlchemy Column Type suitable to store a Json dict."""
    return mutable.MutableDict.as_mutable(JsonEncoded)


def JsonListType():
    """Returns an SQLAlchemy Column Type suitable to store a Json array."""
    return MutableList.as_mutable(JsonEncoded)


def MediumText():
    return sa.Text().with_variant(mysql.MEDIUMTEXT(), 'mysql')


class JsonEncodedMediumText(JsonEncoded):
    impl = MediumText()


def JsonMediumDictType():
    return mutable.MutableDict.as_mutable(JsonEncodedMediumText)


def LongText():
    return sa.Text().with_variant(mysql.LONGTEXT(), 'mysql')


class JsonEncodedLongText(JsonEncoded):
    impl = LongText()


def JsonLongDictType():
    return mutable.MutableDict.as_mutable(JsonEncodedLongText)
