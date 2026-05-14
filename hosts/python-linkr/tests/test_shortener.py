"""Unit tests for short-id generation."""

from __future__ import annotations

import pytest

from app.shortener import (
    ALPHABET,
    SHORT_ID_LEN,
    ShortIDCollision,
    generate_unique_short_id,
    random_short_id,
)


def test_random_short_id_default_length():
    sid = random_short_id()
    assert len(sid) == SHORT_ID_LEN
    assert all(c in ALPHABET for c in sid)


def test_random_short_id_custom_length():
    sid = random_short_id(length=10)
    assert len(sid) == 10


def test_generate_unique_short_id_picks_free_slot():
    # Always free.
    sid = generate_unique_short_id(lambda _c: False)
    assert len(sid) == SHORT_ID_LEN


def test_generate_unique_short_id_retries_then_raises():
    # Always taken -> should raise after max_attempts.
    calls = {"n": 0}

    def always_taken(_c: str) -> bool:
        calls["n"] += 1
        return True

    with pytest.raises(ShortIDCollision):
        generate_unique_short_id(always_taken, max_attempts=3)
    assert calls["n"] == 3


def test_generate_unique_short_id_succeeds_after_collision():
    seen: list[str] = []

    def taken_once(candidate: str) -> bool:
        seen.append(candidate)
        return len(seen) == 1  # only the first candidate is taken

    sid = generate_unique_short_id(taken_once, max_attempts=5)
    assert sid == seen[-1]
    assert len(seen) == 2
