"""SQLAlchemy models and engine setup."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Iterator

from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    short_id: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    hits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


def make_engine(url: str | None = None):
    """Build a SQLAlchemy engine. Defaults to a local SQLite file."""
    db_url = url or os.environ.get("LINKR_DB_URL", "sqlite:///./linkr.db")
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_engine(db_url, connect_args=connect_args, future=True)
    return engine


def make_session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)


def session_dependency(session_factory: sessionmaker[Session]):
    """Build a FastAPI dependency that yields a Session."""

    def _get_db() -> Iterator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    return _get_db
