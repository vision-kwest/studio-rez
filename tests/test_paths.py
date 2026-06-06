from pathlib import Path

from studio_rez import paths


def test_stage_roots_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(tmp_path / "packages"))
    monkeypatch.setenv("STUDIO_PACKAGE_DEV", "/opt/studio/packages/dev")
    monkeypatch.setenv("STUDIO_PACKAGE_TEST", "/opt/studio/packages/test")
    monkeypatch.setenv("STUDIO_PACKAGE_PROD", "/opt/studio/packages/prod")
    monkeypatch.setenv("STUDIO_PACKAGE_ARCHIVE", "/opt/studio/packages/archive")
    assert paths.package_root() == tmp_path / "packages"
    assert paths.dev_root() == tmp_path / "packages" / "dev"
    assert paths.test_root() == tmp_path / "packages" / "test"
    assert paths.prod_root() == tmp_path / "packages" / "prod"
    assert paths.archive_root() == tmp_path / "packages" / "archive"


def test_package_root_reads_environment_at_call_time(monkeypatch, tmp_path):
    first_root = tmp_path / "first" / "packages"
    second_root = tmp_path / "second" / "packages"

    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(first_root))
    assert paths.package_root() == first_root

    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(second_root))
    assert paths.package_root() == second_root
    assert paths.dev_root() == second_root / "dev"


def test_ensure_package_dirs(monkeypatch, tmp_path):
    package_root = tmp_path / "packages"
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(package_root))
    monkeypatch.setenv("STUDIO_PACKAGE_DEV", "/opt/studio/packages/dev")
    monkeypatch.setenv("STUDIO_PACKAGE_TEST", "/opt/studio/packages/test")
    monkeypatch.setenv("STUDIO_PACKAGE_PROD", "/opt/studio/packages/prod")
    monkeypatch.setenv("STUDIO_PACKAGE_ARCHIVE", "/opt/studio/packages/archive")

    created = paths.ensure_package_dirs()

    assert created == [
        package_root / "dev",
        package_root / "test",
        package_root / "prod",
        package_root / "archive",
    ]
    assert all(path.is_dir() for path in created)


def test_package_version_path():
    assert paths.package_version_path(Path("/repo"), "usd", "26.05") == Path("/repo/usd/26.05")
