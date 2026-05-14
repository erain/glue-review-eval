"""FastAPI app factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models import init_db, make_engine, make_session_factory, session_dependency
from app.routes import build_router


def create_app(db_url: str | None = None) -> FastAPI:
    """Build a configured FastAPI app.

    Pass `db_url` to override the SQLite default (handy for tests).
    """
    engine = make_engine(db_url)
    session_factory = make_session_factory(engine)
    get_db = session_dependency(session_factory)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        init_db(engine)
        yield
        engine.dispose()

    app = FastAPI(title="linkr", version="0.1.0", lifespan=lifespan)
    app.include_router(build_router(get_db))

    # Stash engine + factory on the app so tests can override / inspect.
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.get_db = get_db
    return app
