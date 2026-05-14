"""Discover and parse case.yaml sidecars under cases/."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from .config import PATHS

CASE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


@dataclass(frozen=True)
class PlantedFile:
    path: str
    lines: tuple[int, int]
    kind: str


@dataclass(frozen=True)
class Planted:
    description: str
    files: tuple[PlantedFile, ...]


@dataclass(frozen=True)
class Expected:
    must_flag: tuple[str, ...]
    must_not_flag: tuple[str, ...]
    fix_directives: tuple[str, ...]


@dataclass(frozen=True)
class Acceptance:
    setup: tuple[str, ...]
    test_cmd: Optional[str]
    timeout_s: int = 120


@dataclass(frozen=True)
class Case:
    id: str
    language: str
    host: str
    category: str
    severity: str
    title: str
    summary: str
    planted: Optional[Planted]
    expected: Expected
    acceptance: Optional[Acceptance]
    case_dir: Path
    patch_path: Path
    notes: str = ""

    @property
    def patch_diff(self) -> str:
        return self.patch_path.read_text() if self.patch_path.exists() else ""


def _require(d: dict, key: str, where: str):
    if key not in d:
        raise ValueError(f"{where}: missing required field '{key}'")
    return d[key]


def _parse_planted(d: Optional[dict], where: str) -> Optional[Planted]:
    if not d:
        return None
    files = []
    for f in d.get("files") or []:
        lines = f.get("lines", [0, 0])
        files.append(
            PlantedFile(
                path=str(_require(f, "path", f"{where}.planted.files[]")),
                lines=(int(lines[0]), int(lines[1])),
                kind=str(f.get("kind", "")),
            )
        )
    return Planted(
        description=str(d.get("description", "")).strip(),
        files=tuple(files),
    )


def _parse_expected(d: dict, where: str) -> Expected:
    return Expected(
        must_flag=tuple(str(x) for x in (d.get("must_flag") or [])),
        must_not_flag=tuple(str(x) for x in (d.get("must_not_flag") or [])),
        fix_directives=tuple(str(x) for x in (d.get("fix_directives") or [])),
    )


def _parse_acceptance(d: Optional[dict], where: str) -> Optional[Acceptance]:
    if not d:
        return None
    return Acceptance(
        setup=tuple(str(x) for x in (d.get("setup") or [])),
        test_cmd=d.get("test_cmd"),
        timeout_s=int(d.get("timeout_s", 120)),
    )


def parse_case(case_dir: Path) -> Case:
    yaml_path = case_dir / "case.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"no case.yaml in {case_dir}")
    raw = yaml.safe_load(yaml_path.read_text())
    where = str(case_dir.relative_to(PATHS.cases))

    case_id = str(_require(raw, "id", where))
    if not CASE_ID_RE.match(case_id):
        raise ValueError(f"{where}: id {case_id!r} must be kebab-case")

    return Case(
        id=case_id,
        language=str(_require(raw, "language", where)),
        host=str(_require(raw, "host", where)),
        category=str(_require(raw, "category", where)),
        severity=str(_require(raw, "severity", where)),
        title=str(_require(raw, "title", where)),
        summary=str(_require(raw, "summary", where)),
        planted=_parse_planted(raw.get("planted"), where),
        expected=_parse_expected(raw.get("expected") or {}, where),
        acceptance=_parse_acceptance(raw.get("acceptance"), where),
        case_dir=case_dir,
        patch_path=case_dir / "patch.diff",
        notes=str(raw.get("notes", "")),
    )


def discover_cases(root: Path = PATHS.cases) -> list[Case]:
    cases: list[Case] = []
    if not root.exists():
        return cases
    for lang_dir in sorted(root.iterdir()):
        if not lang_dir.is_dir():
            continue
        for case_dir in sorted(lang_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            if not (case_dir / "case.yaml").exists():
                continue
            cases.append(parse_case(case_dir))
    seen = set()
    for c in cases:
        key = (c.language, c.id)
        if key in seen:
            raise ValueError(f"duplicate case id {c.id!r} in {c.language}")
        seen.add(key)
    return cases
