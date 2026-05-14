"""HTTP route handlers for linkr."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.models import Link
from app.schemas import Health, LinkCreate, LinkCreated, LinkDetail
from app.shortener import ShortIDCollision, generate_unique_short_id


def build_router(get_db) -> APIRouter:
    """Create an APIRouter wired to the given DB-session dependency."""
    router = APIRouter()

    @router.get("/healthz", response_model=Health)
    def healthz() -> Health:
        return Health(status="ok")

    @router.post(
        "/links",
        response_model=LinkCreated,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_api_key)],
    )
    def create_link(payload: LinkCreate, db: Session = Depends(get_db)) -> LinkCreated:
        def _exists(candidate: str) -> bool:
            stmt = select(Link.id).where(Link.short_id == candidate)
            return db.execute(stmt).first() is not None

        try:
            short_id = generate_unique_short_id(_exists)
        except ShortIDCollision as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

        link = Link(short_id=short_id, url=str(payload.url))
        db.add(link)
        db.commit()
        db.refresh(link)
        return LinkCreated(short_id=link.short_id, url=link.url)

    @router.get(
        "/links/{short_id}",
        response_model=LinkDetail,
        dependencies=[Depends(require_api_key)],
    )
    def get_link(short_id: str, db: Session = Depends(get_db)) -> LinkDetail:
        link = _load_active_link(db, short_id)
        return LinkDetail.model_validate(link)

    @router.delete(
        "/links/{short_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_api_key)],
    )
    def delete_link(short_id: str, db: Session = Depends(get_db)) -> None:
        from datetime import datetime, timezone

        link = _load_active_link(db, short_id)
        link.deleted_at = datetime.now(timezone.utc)
        db.commit()
        return None

    @router.get("/{short_id}")
    def follow(short_id: str, db: Session = Depends(get_db)) -> RedirectResponse:
        link = _load_active_link(db, short_id)
        link.hits = link.hits + 1
        db.commit()
        return RedirectResponse(url=link.url, status_code=status.HTTP_302_FOUND)

    return router


def _load_active_link(db: Session, short_id: str) -> Link:
    stmt = select(Link).where(Link.short_id == short_id, Link.deleted_at.is_(None))
    link = db.execute(stmt).scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return link
