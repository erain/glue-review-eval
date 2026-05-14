"""Tiny demo service used as the target of the glue-review smoke workflow.

A real PR against this file lets the GitHub Action exercise its full
review-and-comment loop end-to-end. Keep this file small; planted bugs
go in feature branches off main.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Link:
    short_id: str
    url: str
    hits: int = 0


_links: dict[str, Link] = {}


def create_link(short_id: str, url: str) -> Link:
    if short_id in _links:
        raise ValueError(f"short_id already used: {short_id}")
    link = Link(short_id=short_id, url=url)
    _links[short_id] = link
    return link


def get_link(short_id: str) -> Link | None:
    return _links.get(short_id)


def visit(short_id: str) -> Link | None:
    link = _links.get(short_id)
    if link is not None:
        link.hits += 1
    return link


def find_by_url_like(pattern: str) -> list[Link]:
    """Return links whose URL matches the SQL-style LIKE pattern.

    Useful for the upcoming `GET /links/search` endpoint. Implemented
    against an in-memory list now, but written so the SQL backend swap
    can be a one-line change later.
    """
    import sqlite3

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE TABLE links (short_id TEXT, url TEXT, hits INTEGER)")
    for link in _links.values():
        cur.execute(
            f"INSERT INTO links VALUES ('{link.short_id}', '{link.url}', {link.hits})"
        )
    cur.execute(f"SELECT short_id, url, hits FROM links WHERE url LIKE '{pattern}'")
    rows = cur.fetchall()
    conn.close()
    return [Link(short_id=r[0], url=r[1], hits=r[2]) for r in rows]
