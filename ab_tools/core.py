"""Small, dependency-free, auditable utilities for AB pilots."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


class ABError(ValueError):
    """A contract failure, not evidence that a scientific hypothesis is false."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str | Path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: str | Path, payload) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(dest.parent), prefix=".ab_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(raw)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def content_sha256(path: str | Path) -> str:
    sha = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def stable_id(prefix: str, *parts: str) -> str:
    canonical = "\x1f".join(str(p).strip().lower() for p in parts)
    return prefix + "_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def require(obj, spec: dict[str, type], label: str = "record") -> None:
    if not isinstance(obj, dict):
        raise ABError(f"{label} must be an object")
    for key, expected in spec.items():
        if key not in obj:
            raise ABError(f"{label} is missing {key}")
        if expected is int and isinstance(obj[key], bool):
            raise ABError(f"{label}.{key} must be int")
        if not isinstance(obj[key], expected):
            raise ABError(f"{label}.{key} must be {expected.__name__}")


def nonempty(value, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ABError(f"{label} must be a nonempty string")
    return value.strip()
