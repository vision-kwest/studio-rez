"""Validation helpers for Rez package repositories and package.py files."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

PACKAGE_NAME_RE = re.compile(r"^[a-z0-9_]+$")
VERSION_RE = re.compile(r"^\d+(?:\.\d+)*(?:[-+][A-Za-z0-9][A-Za-z0-9_.-]*)?$")
REQUIRED_FIELDS = ("name", "version", "commands")


class ValidationError(ValueError):
    """Raised when a package fails studio Rez validation."""


def validate_package_name(name: str) -> str:
    """Validate and return a Rez package name.

    Studio package names use lowercase ASCII letters, numbers, and underscores.
    """
    if not isinstance(name, str) or not name:
        raise ValidationError("Package name must be a non-empty string.")
    if not PACKAGE_NAME_RE.fullmatch(name):
        raise ValidationError(
            f"Invalid package name '{name}'. Use lowercase letters, numbers, and underscores only."
        )
    return name


def validate_version(version: str) -> str:
    """Validate and return a package version string.

    Accepts SemVer-like versions such as 1.2.3, build/prerelease suffixes, and
    OpenUSD-style versions such as 26.05.
    """
    version_text = str(version)
    if not version_text:
        raise ValidationError("Version must be a non-empty string.")
    if not VERSION_RE.fullmatch(version_text):
        raise ValidationError(
            f"Invalid version '{version_text}'. Use numeric dotted versions like 1.2.3 or 26.05, optionally with -/+ suffixes."
        )
    return version_text


def _load_package_ast(package_py_path: Path) -> ast.Module:
    try:
        return ast.parse(package_py_path.read_text(encoding="utf-8"), filename=str(package_py_path))
    except SyntaxError as exc:
        raise ValidationError(f"{package_py_path} contains invalid Python syntax: {exc}.") from exc
    except OSError as exc:
        raise ValidationError(f"Unable to read {package_py_path}: {exc}.") from exc


def _literal_assignments(tree: ast.Module) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        values[target.id] = ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        values[target.id] = None
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            try:
                values[node.target.id] = ast.literal_eval(node.value) if node.value else None
            except (ValueError, SyntaxError):
                values[node.target.id] = None
    return values


def _function_names(tree: ast.Module) -> set[str]:
    return {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def validate_package_py(path: str | Path) -> Path:
    """Validate that a package.py file exists and return its path."""
    package_py_path = Path(path)
    if package_py_path.is_dir():
        package_py_path = package_py_path / "package.py"
    if not package_py_path.exists():
        raise ValidationError(f"Missing Rez package file: {package_py_path}.")
    if not package_py_path.is_file():
        raise ValidationError(f"Expected a file at {package_py_path}.")
    _load_package_ast(package_py_path)
    return package_py_path


def validate_required_fields(package_py_path: str | Path) -> dict[str, Any]:
    """Validate required Rez package fields and return discovered values."""
    path = validate_package_py(package_py_path)
    tree = _load_package_ast(path)
    assignments = _literal_assignments(tree)
    functions = _function_names(tree)

    missing: list[str] = []
    for field in ("name", "version"):
        if field not in assignments:
            missing.append(field)
    if "commands" not in functions:
        missing.append("commands")
    if missing:
        raise ValidationError(f"{path} is missing required field(s): {', '.join(missing)}.")

    validate_package_name(str(assignments["name"]))
    validate_version(str(assignments["version"]))
    return {"name": assignments["name"], "version": str(assignments["version"]), "commands": True}


def validate_no_spaces_in_paths(path: str | Path) -> Path:
    """Validate that no component in a path contains spaces."""
    candidate = Path(path)
    if any(" " in part for part in candidate.parts):
        raise ValidationError(f"Path contains spaces, which Rez package builds should avoid: {candidate}.")
    return candidate


def validate_package_layout(path: str | Path) -> dict[str, Any]:
    """Validate a package repository layout and return package metadata."""
    package_root = validate_no_spaces_in_paths(path)
    if not package_root.exists():
        raise ValidationError(f"Package repository path does not exist: {package_root}.")
    if not package_root.is_dir():
        raise ValidationError(f"Package repository path is not a directory: {package_root}.")
    package_py = validate_package_py(package_root / "package.py")
    return validate_required_fields(package_py)
