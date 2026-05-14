"""Short-ID generation with uniqueness retry."""

from __future__ import annotations

import secrets
import string
from typing import Callable

ALPHABET = string.ascii_letters + string.digits  # base62
SHORT_ID_LEN = 6
MAX_ATTEMPTS = 8


class ShortIDCollision(RuntimeError):
    """Raised when we cannot find a free short ID within MAX_ATTEMPTS."""


def random_short_id(length: int = SHORT_ID_LEN) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def generate_unique_short_id(
    exists: Callable[[str], bool],
    *,
    length: int = SHORT_ID_LEN,
    max_attempts: int = MAX_ATTEMPTS,
) -> str:
    """Generate a short ID that passes `exists(...)` returning False.

    `exists` is called with each candidate; returning True means the candidate
    is taken. Raises ShortIDCollision after `max_attempts` consecutive hits.
    """
    for _ in range(max_attempts):
        candidate = random_short_id(length)
        if not exists(candidate):
            return candidate
    raise ShortIDCollision(f"could not find a free short id in {max_attempts} attempts")
