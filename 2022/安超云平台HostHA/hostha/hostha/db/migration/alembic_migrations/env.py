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

from __future__ import with_statement
from alembic import context
from logging import config as c
from oslo_utils import importutils
from sqlalchemy import create_engine
from sqlalchemy import pool

from hostha.db.sqlalchemy import model_base


importutils.try_import('hostha.db.sqlalchemy.models')

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
cloudultra_config = config.cloudultra_config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
c.fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support.
target_metadata = model_base.DBModelBase.metadata

# SPDX-License-Identifier: Apache-2.0


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(url=cloudultra_config.database.connection)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = create_engine(
        cloudultra_config.database.connection,
        poolclass=pool.NullPool
    )

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
