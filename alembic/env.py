import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base import Base, engine  # use the app's pre-built engine

# Import all models so Alembic autogenerate discovers them
import app.models  # noqa: F401

config = context.config

# DO NOT use config.set_main_option() — configparser treats % as an
# interpolation character, which breaks any URL-encoded password chars.
# We pass the engine object directly instead.

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Offline mode — no live DB connection.
    Pass the URL object (not a string) so configparser is never involved.
    """
    context.configure(
        url=engine.url,          # SQLAlchemy URL object, bypasses configparser
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Online mode — connect using the app's pre-configured async engine.
    This avoids passing the URL through configparser entirely.
    """
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
