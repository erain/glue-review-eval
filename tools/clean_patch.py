#!/usr/bin/env python3
"""Filter out runtime/build artefacts (pycache, .pyc, *.db, .venv, node_modules)
from a unified diff that was captured before stage_case.sh learned to
gitignore them. Reads stdin, writes stdout."""

from __future__ import annotations

import re
import sys

DROP_PATTERNS = [
    re.compile(r"(^| )b/(?:[^ \n]*/)?__pycache__/"),
    re.compile(r"(^| )b/(?:[^ \n]*/)?\.pytest_cache/"),
    re.compile(r"(^| )b/(?:[^ \n]*/)?\.venv/"),
    re.compile(r"(^| )b/(?:[^ \n]*/)?node_modules/"),
    re.compile(r"(^| )b/(?:[^ \n]*/)?\.next/"),
    re.compile(r"(^| )b/(?:[^ \n]*/)?dist/"),
    re.compile(r"\.pyc\b"),
    re.compile(r"\.pyo\b"),
    re.compile(r"\.db(-journal)?\b"),
]


def should_drop_section(header_line: str) -> bool:
    return any(p.search(header_line) for p in DROP_PATTERNS)


def main() -> int:
    text = sys.stdin.read()
    out: list[str] = []
    current_block: list[str] = []
    keep_current = True

    def flush():
        if keep_current and current_block:
            out.extend(current_block)
        current_block.clear()

    for line in text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            flush()
            keep_current = not should_drop_section(line)
            current_block.append(line)
        else:
            current_block.append(line)
    flush()
    sys.stdout.write("".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
