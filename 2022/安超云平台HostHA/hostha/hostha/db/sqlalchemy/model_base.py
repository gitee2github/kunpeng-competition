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

from sqlalchemy.ext import declarative
from sqlalchemy.orm import attributes
from oslo_db.sqlalchemy import models as oslo_models

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2013 Mirantis Inc.


class _ModelBase(oslo_models.ModelBase):
    """Base class for all SQLAlchemy DB Models."""

    def to_dict(self):
        """sqlalchemy based automatic to_dict method."""
        d = {}

        # if a column is unloaded at this point, it is
        # probably deferred. We do not want to access it
        # here and thereby cause it to load...
        unloaded = attributes.instance_state(self).unloaded

        for col in self.__table__.columns:
            if col.name not in unloaded:
                d[col.name] = getattr(self, col.name)

        datetime_to_str(d, 'created_at')
        datetime_to_str(d, 'updated_at')
        datetime_to_str(d, 'state_updated_at')

        return d

    def save(self, session=None):
        if session is None:
            import hostha.db.sqlalchemy.api as db_api
            session = db_api.get_session()

        super(_ModelBase, self).save(session)


def datetime_to_str(dct, attr_name):
    if dct.get(attr_name) is not None:
        value = dct[attr_name].isoformat('T')
        ms_delimiter = value.find(".")
        if ms_delimiter != -1:
            # Removing ms from time
            value = value[:ms_delimiter]
        dct[attr_name] = value


DBModelBase = declarative.declarative_base(cls=_ModelBase)
