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

import uuid

import six
import sqlalchemy as sa

from hostha.db.sqlalchemy import model_base as mb
from hostha.db.sqlalchemy import types as st
from oslo_log import log

LOG = log.getLogger(__name__)


def _generate_unicode_uuid():
    return six.text_type(uuid.uuid4())


def _id_column():
    return sa.Column(sa.String(36),
                     primary_key=True,
                     default=_generate_unicode_uuid)


class Configuration(mb.DBModelBase):
    """Represents host and vm ha config"""

    __tablename__ = "configuration"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    group = sa.Column(sa.String(255), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    value = sa.Column(sa.String(255), nullable=True)


class HAHost(mb.DBModelBase):
    """Represents compute host data"""

    __tablename__ = "ha_host"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    hostname = sa.Column(sa.String(255), nullable=False)
    task = sa.Column(sa.String(255), nullable=True)
    host_ha_enabled = sa.Column(sa.Integer(), nullable=True)
    ipmi_ip = sa.Column(sa.String(255), nullable=True)
    ipmi_user = sa.Column(sa.String(255), nullable=True)
    ipmi_password = sa.Column(sa.String(255), nullable=True)
    last_health = sa.Column(st.JsonDictType(), nullable=False, default={})


class HAHostEvacuation(mb.DBModelBase):
    """Represents an host evacuation data"""

    __tablename__ = "ha_host_evacuation"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    hostname = sa.Column(sa.String(255), nullable=False)
    started_at = sa.Column(sa.DateTime(), nullable=True)
    finished_at = sa.Column(sa.DateTime(), nullable=True)


class HostVmEvacuation(mb.DBModelBase):
    """Represents an host vm evacuation data"""

    __tablename__ = "host_vm_evacuation"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    vm_uuid = sa.Column(sa.String(255), nullable=False)
    vm_name = sa.Column(sa.String(255), nullable=True)
    src_host = sa.Column(sa.String(255), nullable=True)
    des_host = sa.Column(sa.String(255), nullable=True)
    started_at = sa.Column(sa.DateTime(), nullable=True)
    finished_at = sa.Column(sa.DateTime(), nullable=True)
    result = sa.Column(sa.Integer(), nullable=True)
    message = sa.Column(sa.String(255), nullable=True)
    host_op_id = sa.Column(sa.Integer(), nullable=True)
    retry_count = sa.Column(sa.Integer(), nullable=True)
    origin_state = sa.Column(sa.String(255), nullable=True)
