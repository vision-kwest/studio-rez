"""Path helpers for the studio Rez package repositories."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PACKAGE_ROOT = Path("/opt/studio/packages")
STAGE_NAMES = ("dev", "test", "prod", "archive")


def package_root() -> Path:
    """Return the configured root containing all package stage repositories."""
    return Path(os.environ.get("STUDIO_PACKAGE_ROOT", DEFAULT_PACKAGE_ROOT)).expanduser()


def dev_root() -> Path:
    """Return the development package repository path."""
    return Path(os.environ.get("STUDIO_PACKAGE_DEV", package_root() / "dev")).expanduser()


def test_root() -> Path:
    """Return the test package repository path."""
    return Path(os.environ.get("STUDIO_PACKAGE_TEST", package_root() / "test")).expanduser()


def prod_root() -> Path:
    """Return the production package repository path."""
    return Path(os.environ.get("STUDIO_PACKAGE_PROD", package_root() / "prod")).expanduser()


def archive_root() -> Path:
    """Return the archived package repository path."""
    return Path(os.environ.get("STUDIO_PACKAGE_ARCHIVE", package_root() / "archive")).expanduser()


def stage_root(stage: str) -> Path:
    """Return the repository root for a supported stage name."""
    roots = {
        "dev": dev_root,
        "test": test_root,
        "prod": prod_root,
        "archive": archive_root,
    }
    try:
        return roots[stage]()
    except KeyError as exc:
        supported = ", ".join(sorted(roots))
        raise ValueError(f"Unsupported package stage '{stage}'. Expected one of: {supported}.") from exc


def ensure_package_dirs() -> list[Path]:
    """Create all standard stage directories and return them."""
    roots = [dev_root(), test_root(), prod_root(), archive_root()]
    for root in roots:
        root.mkdir(parents=True, exist_ok=True)
    return roots


def package_family_path(root: os.PathLike[str] | str, name: str) -> Path:
    """Return the family directory for a package name under a repository root."""
    return Path(root).expanduser() / name


def package_version_path(root: os.PathLike[str] | str, name: str, version: str) -> Path:
    """Return the immutable package version directory under a repository root."""
    return package_family_path(root, name) / str(version)
