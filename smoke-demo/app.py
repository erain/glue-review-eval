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
