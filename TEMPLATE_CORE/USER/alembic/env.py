"""Alembic environment for agent-generated migrations.

Because ``user_core`` ships only abstract models, this env.py is a template.
Agents must import their concrete model modules BEFORE ``target_metadata``
is read, so Alembic sees the real table definitions::

    # Add this block after the user_core imports:
    import myapp.models  # noqa: F401 — registers concrete tables with Base

Without that import, ``Base.metadata`` is empty and autogenerate produces
no migrations.
"""
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

from user_core.db import Base  # noqa: E402

# ── AGENT: import your concrete model modules here ──────────────────────────
# import myapp.models  # registers tables with Base.metadata
# ────────────────────────────────────────────────────────────────────────────

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
