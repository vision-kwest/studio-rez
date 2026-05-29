"""JSON manifest helpers for studio Rez package builds."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_manifest(path: str | Path, data: dict[str, Any]) -> Path:
    """Write manifest data as stable, human-readable JSON and return the path."""
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def read_manifest(path: str | Path) -> dict[str, Any]:
    """Read a JSON manifest from disk."""
    manifest_path = Path(path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON manifest at {manifest_path}: {exc}.") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Manifest at {manifest_path} must contain a JSON object.")
    return data


def create_build_manifest(
    package_name: str,
    version: str,
    source_repo: str,
    source_commit: str,
    build_image: str,
    build_time: str,
) -> dict[str, str]:
    """Create a standard build provenance manifest."""
    return {
        "package_name": package_name,
        "version": str(version),
        "source_repo": source_repo,
        "source_commit": source_commit,
        "build_image": build_image,
        "build_time": build_time,
    }
