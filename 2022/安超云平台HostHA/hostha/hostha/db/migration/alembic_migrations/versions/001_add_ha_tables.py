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

"""Add ha tables

Revision ID: 001
Revises: None
Create Date: 2021-10/08 12:00:00.000000
"""

# revision identifiers, used by Alembic.

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from hostha.db.sqlalchemy import types as st
MYSQL_ENGINE = "InnoDB"
MYSQL_CHARSET = "utf8"
revision = "001"
down_revision = None


def upgrade():
    op.create_table(
        "configuration",
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column("group", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("value", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )

    config_table = table(
        'configuration',
        column('id', sa.Integer),
        column("group", sa.String(255)),
        column("name", sa.String(255)),
        column("value", sa.String(255))
    )

    op.bulk_insert(
        config_table,
        [
            {'group': 'host_ha', 'name': 'check_interval', 'value': '20'},
            {'group': 'host_ha', 'name': 'check_retry', 'value': '3'},
        ]
    )

    op.create_table(
        "ha_host",
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column("task", sa.String(255), nullable=True),
        sa.Column("host_ha_enabled", sa.Integer(), nullable=True),
        sa.Column("ipmi_ip", sa.String(255), nullable=True),
        sa.Column("ipmi_user", sa.String(255), nullable=True),
        sa.Column("ipmi_password", sa.String(255), nullable=True),
        sa.Column('last_health', st.JsonEncoded(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )

    op.create_table(
        "ha_host_evacuation",
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )

    op.create_table(
        "host_vm_evacuation",
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column("vm_uuid", sa.String(255), nullable=False),
        sa.Column("vm_name", sa.String(255), nullable=True),
        sa.Column("src_host", sa.String(255), nullable=True),
        sa.Column("des_host", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("result", sa.Integer(), nullable=True),
        sa.Column("message", sa.String(255), nullable=True),
        sa.Column("host_op_id", sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('origin_state', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine=MYSQL_ENGINE,
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    op.drop_table('configuration')
    op.drop_table('ha_host')
    op.drop_table('ha_host_evacuation')
    op.drop_table('ha_vm_evacuation')
