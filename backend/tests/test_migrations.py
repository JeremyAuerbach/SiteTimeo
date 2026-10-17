"""Les migrations Alembic, sur une vraie base PostgreSQL (TEST_DATABASE_URL)."""

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from alembic import command
from alembic.config import Config

pytestmark = pytest.mark.skipif(
    not os.environ["DATABASE_URL"].startswith("postgresql"),
    reason="migrations testées sur PostgreSQL uniquement (définir TEST_DATABASE_URL)",
)

BACKEND = Path(__file__).resolve().parents[1]


def alembic_config() -> Config:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    return config


def tables() -> set[str]:
    engine = create_engine(os.environ["DATABASE_URL"])
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_migrations_upgrade_match_models_and_downgrade():
    config = alembic_config()
    try:
        command.upgrade(config, "head")
        assert {"users", "auth_sessions", "user_avatars"} <= tables()
        # Échoue si un modèle a changé sans migration correspondante.
        command.check(config)

        # Chaque downgrade défait bien son upgrade, et on peut remonter ensuite.
        command.downgrade(config, "base")
        assert tables() == {"alembic_version"}
        command.upgrade(config, "head")
    finally:
        command.downgrade(config, "base")
        engine = create_engine(os.environ["DATABASE_URL"])
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        engine.dispose()
