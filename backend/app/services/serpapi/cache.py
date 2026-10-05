from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_TTLS = {
    "google_news": timedelta(hours=3),
    "google": timedelta(hours=12),
    "google_trends": timedelta(hours=24),
    "google_scholar": timedelta(hours=48),
    "google_patents": timedelta(hours=72),
}


def query_fingerprint(engine: str, params: dict[str, Any]) -> str:
    safe_params = {
        key: value
        for key, value in params.items()
        if key not in {"api_key", "no_cache"}
    }
    canonical = json.dumps(
        {"engine": engine, "params": safe_params},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CacheHit:
    fingerprint: str
    payload: dict[str, Any]
    stored_at: datetime


class FileSearchCache:
    def __init__(self, root: Path) -> None:
        self.root = root

    def get(self, *, engine: str, params: dict[str, Any]) -> CacheHit | None:
        fingerprint = query_fingerprint(engine, params)
        path = self._path(fingerprint)
        if not path.exists():
            return None

        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            stored_at = datetime.fromisoformat(record["stored_at"])
            if stored_at.tzinfo is None:
                stored_at = stored_at.replace(tzinfo=UTC)
            ttl = DEFAULT_TTLS.get(engine, timedelta(hours=12))
            if datetime.now(UTC) - stored_at > ttl:
                path.unlink(missing_ok=True)
                return None
            payload = record["payload"]
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            path.unlink(missing_ok=True)
            return None

        if not isinstance(payload, dict):
            path.unlink(missing_ok=True)
            return None

        return CacheHit(fingerprint=fingerprint, payload=payload, stored_at=stored_at)

    def put(self, *, engine: str, params: dict[str, Any], payload: dict[str, Any]) -> str:
        fingerprint = query_fingerprint(engine, params)
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path(fingerprint)
        temporary_path = path.with_suffix(".tmp")
        record = {
            "engine": engine,
            "stored_at": datetime.now(UTC).isoformat(),
            "payload": payload,
        }
        temporary_path.write_text(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        temporary_path.replace(path)
        return fingerprint

    def _path(self, fingerprint: str) -> Path:
        return self.root / f"{fingerprint}.json"
