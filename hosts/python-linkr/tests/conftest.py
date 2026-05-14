"""Test fixtures: in-memory SQLite + test client with API key configured."""

from __future__ import annotations

from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.models import Base, make_session_factory, session_dependency

API_KEY = "test-key"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("LINKR_API_KEY", API_KEY)

    # Shared in-memory SQLite: StaticPool keeps a single connection alive so
    # every session sees the same schema and rows.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    session_factory = make_session_factory(engine)

    application = create_app()
    # Replace the per-request session dependency with one bound to our engine.
    application.dependency_overrides[application.state.get_db] = session_dependency(
        session_factory
    )
    application.state.engine = engine
    application.state.session_factory = session_factory
    yield application
    engine.dispose()


@pytest.fixture
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY}


@pytest.fixture
def db_session(app) -> Iterator[Session]:
    factory = app.state.session_factory
    s = factory()
    try:
        yield s
    finally:
        s.close()
