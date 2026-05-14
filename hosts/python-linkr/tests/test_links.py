"""Integration tests covering link CRUD, auth, redirects, and soft-delete."""

from __future__ import annotations

import pytest


def _create(client, headers, url="https://example.com/hello"):
    r = client.post("/links", json={"url": url}, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_create_link_happy_path(client, auth_headers):
    body = _create(client, auth_headers, "https://example.com/foo")
    assert "short_id" in body
    assert len(body["short_id"]) == 6
    assert body["url"] == "https://example.com/foo"


def test_create_link_requires_api_key(client):
    r = client.post("/links", json={"url": "https://example.com"})
    assert r.status_code == 401


def test_create_link_rejects_bad_key(client):
    r = client.post(
        "/links",
        json={"url": "https://example.com"},
        headers={"X-API-Key": "nope"},
    )
    assert r.status_code == 401


def test_create_link_validates_url(client, auth_headers):
    r = client.post("/links", json={"url": "not-a-url"}, headers=auth_headers)
    assert r.status_code == 422


def test_get_link_returns_metadata(client, auth_headers):
    created = _create(client, auth_headers, "https://example.com/meta")
    r = client.get(f"/links/{created['short_id']}", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["short_id"] == created["short_id"]
    assert body["url"] == "https://example.com/meta"
    assert body["hits"] == 0
    assert "created_at" in body


def test_get_link_requires_api_key(client, auth_headers):
    created = _create(client, auth_headers)
    r = client.get(f"/links/{created['short_id']}")
    assert r.status_code == 401


def test_get_link_404(client, auth_headers):
    r = client.get("/links/zzzzzz", headers=auth_headers)
    assert r.status_code == 404


def test_redirect_returns_302_and_increments_hits(client, auth_headers):
    created = _create(client, auth_headers, "https://example.com/redirect")
    sid = created["short_id"]

    r = client.get(f"/{sid}", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "https://example.com/redirect"

    r2 = client.get(f"/{sid}", follow_redirects=False)
    assert r2.status_code == 302

    detail = client.get(f"/links/{sid}", headers=auth_headers).json()
    assert detail["hits"] == 2


def test_redirect_no_auth_required(client, auth_headers):
    created = _create(client, auth_headers)
    r = client.get(f"/{created['short_id']}", follow_redirects=False)
    assert r.status_code == 302


def test_redirect_unknown_404(client):
    r = client.get("/zzzzzz", follow_redirects=False)
    assert r.status_code == 404


def test_delete_link_soft_deletes(client, auth_headers):
    created = _create(client, auth_headers, "https://example.com/del")
    sid = created["short_id"]

    r = client.delete(f"/links/{sid}", headers=auth_headers)
    assert r.status_code == 204

    # Further fetches 404.
    assert client.get(f"/links/{sid}", headers=auth_headers).status_code == 404
    assert client.get(f"/{sid}", follow_redirects=False).status_code == 404


def test_delete_requires_api_key(client, auth_headers):
    created = _create(client, auth_headers)
    r = client.delete(f"/links/{created['short_id']}")
    assert r.status_code == 401


def test_delete_unknown_404(client, auth_headers):
    r = client.delete("/links/zzzzzz", headers=auth_headers)
    assert r.status_code == 404


def test_soft_delete_row_still_present(client, auth_headers, db_session):
    from sqlalchemy import select

    from app.models import Link

    created = _create(client, auth_headers, "https://example.com/persist")
    client.delete(f"/links/{created['short_id']}", headers=auth_headers)

    row = db_session.execute(
        select(Link).where(Link.short_id == created["short_id"])
    ).scalar_one()
    assert row.deleted_at is not None


def test_missing_api_key_env_returns_503(client, monkeypatch):
    monkeypatch.delenv("LINKR_API_KEY", raising=False)
    r = client.post(
        "/links",
        json={"url": "https://example.com"},
        headers={"X-API-Key": "anything"},
    )
    assert r.status_code == 503


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/a",
        "http://example.com/b",
        "https://sub.example.com/c?x=1&y=2",
    ],
)
def test_create_link_accepts_various_urls(client, auth_headers, url):
    body = _create(client, auth_headers, url)
    assert body["url"] == url
