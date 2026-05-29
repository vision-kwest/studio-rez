from pathlib import Path

from studio_rez import paths


def test_stage_roots_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(tmp_path / "packages"))
    monkeypatch.delenv("STUDIO_PACKAGE_DEV", raising=False)
    monkeypatch.delenv("STUDIO_PACKAGE_TEST", raising=False)
    monkeypatch.delenv("STUDIO_PACKAGE_PROD", raising=False)
    monkeypatch.delenv("STUDIO_PACKAGE_ARCHIVE", raising=False)
    assert paths.package_root() == tmp_path / "packages"
    assert paths.dev_root() == tmp_path / "packages" / "dev"
    assert paths.test_root() == tmp_path / "packages" / "test"
    assert paths.prod_root() == tmp_path / "packages" / "prod"
    assert paths.archive_root() == tmp_path / "packages" / "archive"


def test_ensure_package_dirs(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(tmp_path / "packages"))
    created = paths.ensure_package_dirs()
    assert {path.name for path in created} == {"dev", "test", "prod", "archive"}
    assert all(path.is_dir() for path in created)


def test_package_version_path():
    assert paths.package_version_path(Path("/repo"), "usd", "26.05") == Path("/repo/usd/26.05")
