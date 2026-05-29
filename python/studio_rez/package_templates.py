"""Package skeleton creation helpers."""

from __future__ import annotations

from pathlib import Path

from studio_rez.validation import validate_package_name, validate_version

TEMPLATE_FILES = {
    "generic": "package.py.template",
    "python": "python-package.py.template",
    "binary": "binary-package.py.template",
    "dcc": "dcc-package.py.template",
}


def repo_root() -> Path:
    """Return the studio-rez repository root inferred from this module path."""
    return Path(__file__).resolve().parents[2]


def render_template(template_text: str, name: str, version: str) -> str:
    """Render the simple package templates used by this repository."""
    return template_text.replace("{{name}}", name).replace("{{version}}", version)


def create_package_skeleton(
    name: str,
    package_type: str = "generic",
    version: str = "0.1.0",
    destination: str | Path | None = None,
) -> Path:
    """Create a Rez package skeleton and return the created directory."""
    package_name = validate_package_name(name)
    package_version = validate_version(version)
    if package_type not in TEMPLATE_FILES:
        supported = ", ".join(sorted(TEMPLATE_FILES))
        raise ValueError(f"Unsupported package type '{package_type}'. Expected one of: {supported}.")

    dest = Path(destination) if destination is not None else Path.cwd() / package_name
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f"Destination already exists and is not empty: {dest}.")
    dest.mkdir(parents=True, exist_ok=True)

    template_path = repo_root() / "templates" / TEMPLATE_FILES[package_type]
    package_text = render_template(template_path.read_text(encoding="utf-8"), package_name, package_version)
    (dest / "package.py").write_text(package_text, encoding="utf-8")

    if package_type in {"python", "dcc"}:
        module_dir = dest / "python" / package_name
        module_dir.mkdir(parents=True, exist_ok=True)
        (module_dir / "__init__.py").write_text(f'"""{package_name} package."""\n', encoding="utf-8")
    if package_type == "binary":
        bin_dir = dest / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        readme = bin_dir / ".gitkeep"
        readme.write_text("", encoding="utf-8")
    return dest
