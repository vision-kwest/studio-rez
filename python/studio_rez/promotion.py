"""Promotion helpers for immutable Rez package versions."""

from __future__ import annotations

import shutil
from pathlib import Path

from studio_rez.paths import package_version_path, stage_root
from studio_rez.validation import validate_package_name, validate_version

SUPPORTED_STAGES = ("dev", "test", "prod", "archive")


def promote_package(
    name: str,
    version: str,
    source_stage: str,
    dest_stage: str,
    dry_run: bool = False,
) -> dict[str, str | bool]:
    """Copy an immutable package version from one stage repository to another.

    Existing destination package versions are never overwritten.
    """
    package_name = validate_package_name(name)
    package_version = validate_version(str(version))
    source_root = stage_root(source_stage)
    dest_root = stage_root(dest_stage)
    source = package_version_path(source_root, package_name, package_version)
    dest = package_version_path(dest_root, package_name, package_version)

    if source_stage == dest_stage:
        raise ValueError("Source and destination stages must be different.")
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"Source package version does not exist: {source}.")
    if dest.exists():
        raise FileExistsError(f"Destination package version already exists and will not be overwritten: {dest}.")

    result: dict[str, str | bool] = {
        "name": package_name,
        "version": package_version,
        "source_stage": source_stage,
        "dest_stage": dest_stage,
        "source": str(source),
        "destination": str(dest),
        "dry_run": dry_run,
    }
    if dry_run:
        return result

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, symlinks=True)
    return result
