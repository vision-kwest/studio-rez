"""Opt-in prototype: publish one package payload and link approved stages to it.

Not a replacement for the existing copy-based promotion CLI.
"""
from __future__ import annotations

import argparse
import os
import shutil
import uuid
from pathlib import Path

from studio_rez.paths import package_root
from studio_rez.validation import validate_package_name, validate_version


def publish_artifact(name: str, version: str, artifact_id: str, root: Path | None = None) -> Path:
    """Copy dev once to a distinct artifact; never overwrite an existing artifact."""
    name, version = validate_package_name(name), validate_version(version)
    artifact_id = validate_package_name(artifact_id)
    root = root or package_root()
    source = root / "dev" / name / version
    target = root / "artifacts" / name / version / artifact_id
    if not source.is_dir() or not (source / "package.py").is_file():
        raise FileNotFoundError(f"Missing source Rez package: {source}")
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Artifact already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.parent / f".{artifact_id}.{uuid.uuid4().hex}.tmp"
    try:
        shutil.copytree(source, temp, symlinks=True)
        # os.rename does not replace an existing nonempty directory on Linux.
        # The unique artifact path is never reused by this prototype.
        os.rename(temp, target)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return target


def promote_link(name: str, version: str, artifact_id: str, stage: str, root: Path | None = None) -> Path:
    """Create-only stage selection. Stage entries are never replaced."""
    name, version = validate_package_name(name), validate_version(version)
    artifact_id = validate_package_name(artifact_id)
    if stage not in ("test", "prod", "archive"):
        raise ValueError("Prototype supports only test, prod and archive")
    root = root or package_root()
    artifact = root / "artifacts" / name / version / artifact_id
    if not artifact.is_dir() or not (artifact / "package.py").is_file():
        raise FileNotFoundError(f"Missing artifact: {artifact}")
    destination = root / stage / name / version
    destination.parent.mkdir(parents=True, exist_ok=True)
    # POSIX symlink creation is atomic and fails when destination exists.
    destination.symlink_to(os.path.relpath(artifact, destination.parent), target_is_directory=True)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimental symlink promotion (Issue #6)")
    parser.add_argument("action", choices=("publish", "link"))
    parser.add_argument("name")
    parser.add_argument("version")
    parser.add_argument("artifact_id", help="Unique immutable build identifier (lowercase letters, digits, underscores)")
    parser.add_argument("--stage", choices=("test", "prod", "archive"))
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    if args.action == "publish":
        print(publish_artifact(args.name, args.version, args.artifact_id, args.root))
    else:
        if not args.stage:
            parser.error("--stage required for link")
        print(promote_link(args.name, args.version, args.artifact_id, args.stage, args.root))


if __name__ == "__main__":
    main()
