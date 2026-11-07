"""Promotion helpers for immutable Rez package versions."""
from __future__ import annotations

import os
from pathlib import Path

from studio_rez.paths import package_root, package_version_path, stage_root
from studio_rez.validation import validate_package_name, validate_version

SUPPORTED_STAGES = ("dev", "test", "prod", "archive")


def promote_package(
    name: str,
    version: str,
    source_stage: str,
    dest_stage: str,
    dry_run: bool = False,
) -> dict[str, str | bool]:
    """Promote by reference; retain the existing CLI and no-overwrite contract."""
    package_name = validate_package_name(name)
    package_version = validate_version(str(version))
    source = package_version_path(stage_root(source_stage), package_name, package_version)
    dest = package_version_path(stage_root(dest_stage), package_name, package_version)
    artifact = package_root() / "artifacts" / package_name / package_version / "published"

    if source_stage == dest_stage:
        raise ValueError("Source and destination stages must be different.")
    if not source.is_dir() or not (source / "package.py").is_file():
        raise FileNotFoundError(f"Source package version does not exist: {source}.")
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(f"Destination package version already exists: {dest}.")

    result: dict[str, str | bool] = {
        "name": package_name, "version": package_version,
        "source_stage": source_stage, "dest_stage": dest_stage,
        "source": str(source), "destination": str(dest), "dry_run": dry_run,
    }
    if dry_run:
        return result

    if not source.is_symlink():
        if source_stage != "dev":
            raise ValueError("Only a dev package can be frozen into the artifact store.")
        artifact.parent.mkdir(parents=True, exist_ok=True)
        if artifact.exists() or artifact.is_symlink():
            raise FileExistsError(f"Artifact already exists: {artifact}")
        # Same-EFS rename: no second payload copy.
        source.rename(artifact)
        try:
            source.symlink_to(os.path.relpath(artifact, source.parent), target_is_directory=True)
        except BaseException:
            artifact.rename(source)
            raise
    else:
        if source.resolve() != artifact.resolve() or not artifact.is_dir():
            raise ValueError(f"Source does not reference the expected artifact: {source}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.symlink_to(os.path.relpath(artifact, dest.parent), target_is_directory=True)
    return result
