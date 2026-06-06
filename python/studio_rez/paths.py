"""Path helpers for the studio Rez package repositories.

The important rule for this module is that runtime environment variables must be
read at *function call time*, not cached when the module is imported. Studio Rez
shell setup files are commonly sourced before commands run, but tests also use
pytest's monkeypatch fixture to swap environment variables inside the same Python
process. If a path is captured as a module-level constant, a later monkeypatch of
``STUDIO_PACKAGE_ROOT`` is invisible and callers can accidentally write to the
site default (``/opt/studio/packages``) instead of the requested test/runtime
location.
"""

from __future__ import annotations

import os
from pathlib import Path

# This is only the fallback value used when STUDIO_PACKAGE_ROOT is unset. Keep it
# clearly named as a default so future edits do not turn it into a cached runtime
# root. The active root is always resolved through package_root().
DEFAULT_PACKAGE_ROOT = Path("/opt/studio/packages")

# Keep the canonical stage names in one place for callers that need to present or
# iterate over the standard repositories. The actual Path for each stage is still
# resolved dynamically below so it follows the current STUDIO_PACKAGE_ROOT.
STAGE_NAMES = ("dev", "test", "prod", "archive")


def package_root() -> Path:
    """Return the configured root containing all package stage repositories."""
    # Read os.environ on every call so runtime changes made by sourced shells,
    # subprocess env overrides, or pytest monkeypatch are honored immediately.
    return Path(os.environ.get("STUDIO_PACKAGE_ROOT", DEFAULT_PACKAGE_ROOT)).expanduser()


def dev_root() -> Path:
    """Return the development package repository path."""
    # Deliberately derive from package_root() instead of STUDIO_PACKAGE_DEV.
    # env/studio-dev.sh exports stage-specific variables for shell convenience,
    # but those values can become stale if STUDIO_PACKAGE_ROOT changes later in a
    # long-lived Python process or a test. The repo contract is that the four
    # standard stages live under the current package root.
    return package_root() / "dev"


def test_root() -> Path:
    """Return the test package repository path."""
    # See dev_root(): all stage helpers must re-read STUDIO_PACKAGE_ROOT via
    # package_root() at call time and then append their stage name.
    return package_root() / "test"


def prod_root() -> Path:
    """Return the production package repository path."""
    # Production packages are part of the same standard root layout as dev/test.
    # Do not cache or independently override this path; promotion depends on all
    # stages resolving from one coherent package root.
    return package_root() / "prod"


def archive_root() -> Path:
    """Return the archived package repository path."""
    # Archive is also rooted under the dynamic package_root() so cleanup and
    # promotion workflows follow STUDIO_PACKAGE_ROOT consistently.
    return package_root() / "archive"


def stage_root(stage: str) -> Path:
    """Return the repository root for a supported stage name."""
    # Store callables, not Paths. This is subtle but important: constructing the
    # dictionary must not freeze the path values. Each lookup invokes the helper
    # for the requested stage and therefore sees the current environment.
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
    """Create all standard stage directories under the current package root and return them."""
    # Resolve the roots immediately before creation so a caller can set
    # STUDIO_PACKAGE_ROOT moments before calling this function and get exactly
    # the directories they asked for. This prevents test runs and EC2 bootstrap
    # commands from falling back to /opt/studio/packages unexpectedly.
    roots = [dev_root(), test_root(), prod_root(), archive_root()]
    for root in roots:
        root.mkdir(parents=True, exist_ok=True)
    return roots


def package_family_path(root: os.PathLike[str] | str, name: str) -> Path:
    """Return the family directory for a package name under a repository root."""
    # The root argument is intentionally explicit here. Higher-level code chooses
    # the dynamic stage root first, then this helper appends the package family.
    return Path(root).expanduser() / name


def package_version_path(root: os.PathLike[str] | str, name: str, version: str) -> Path:
    """Return the immutable package version directory under a repository root."""
    # Version directories are immutable Rez payload locations. This helper only
    # composes path segments; it does not inspect the environment directly.
    return package_family_path(root, name) / str(version)
