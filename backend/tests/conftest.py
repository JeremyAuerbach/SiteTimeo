import os

# Base dédiée aux tests ; à surcharger via TEST_DATABASE_URL pour viser PostgreSQL.
os.environ.setdefault("DATABASE_URL", os.environ.get("TEST_DATABASE_URL", "sqlite://"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def session_factory():
    url = os.environ["DATABASE_URL"]
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        # SQLite n'applique les clés étrangères (et donc ON DELETE CASCADE) que sur demande.
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    else:
        engine = create_engine(url)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
