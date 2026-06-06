from pathlib import Path

from studio_rez import paths


def test_stage_roots_from_environment(monkeypatch, tmp_path):
    # Regression guard for sourced shell environments: env/studio-dev.sh exports
    # STUDIO_PACKAGE_DEV/TEST/PROD/ARCHIVE based on whatever root existed at
    # source time. A later STUDIO_PACKAGE_ROOT override must win so tests and
    # subprocesses do not keep writing to /opt/studio/packages.
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(tmp_path / "packages"))
    monkeypatch.setenv("STUDIO_PACKAGE_DEV", "/opt/studio/packages/dev")
    monkeypatch.setenv("STUDIO_PACKAGE_TEST", "/opt/studio/packages/test")
    monkeypatch.setenv("STUDIO_PACKAGE_PROD", "/opt/studio/packages/prod")
    monkeypatch.setenv("STUDIO_PACKAGE_ARCHIVE", "/opt/studio/packages/archive")

    # Each stage helper should derive from the current package_root() value, not
    # from the stale stage-specific variables above.
    assert paths.package_root() == tmp_path / "packages"
    assert paths.dev_root() == tmp_path / "packages" / "dev"
    assert paths.test_root() == tmp_path / "packages" / "test"
    assert paths.prod_root() == tmp_path / "packages" / "prod"
    assert paths.archive_root() == tmp_path / "packages" / "archive"


def test_package_root_reads_environment_at_call_time(monkeypatch, tmp_path):
    # This mirrors pytest's intended monkeypatch use case: mutate os.environ in a
    # running Python process and expect code under test to observe the new value.
    # If package_root() ever becomes an import-time constant, the second assert
    # below will catch the stale cached value.
    first_root = tmp_path / "first" / "packages"
    second_root = tmp_path / "second" / "packages"

    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(first_root))
    assert paths.package_root() == first_root

    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(second_root))
    assert paths.package_root() == second_root
    assert paths.dev_root() == second_root / "dev"


def test_ensure_package_dirs(monkeypatch, tmp_path):
    # ensure_package_dirs() performs writes, so this is the most important guard
    # against accidentally creating /opt/studio/packages/dev on developer or CI
    # machines after a test monkeypatches STUDIO_PACKAGE_ROOT.
    package_root = tmp_path / "packages"
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(package_root))
    monkeypatch.setenv("STUDIO_PACKAGE_DEV", "/opt/studio/packages/dev")
    monkeypatch.setenv("STUDIO_PACKAGE_TEST", "/opt/studio/packages/test")
    monkeypatch.setenv("STUDIO_PACKAGE_PROD", "/opt/studio/packages/prod")
    monkeypatch.setenv("STUDIO_PACKAGE_ARCHIVE", "/opt/studio/packages/archive")

    created = paths.ensure_package_dirs()

    # Assert exact paths and ordering, not just names, so stale roots cannot hide
    # behind the same dev/test/prod/archive basename set.
    assert created == [
        package_root / "dev",
        package_root / "test",
        package_root / "prod",
        package_root / "archive",
    ]
    assert all(path.is_dir() for path in created)


def test_package_version_path():
    # This helper intentionally composes an explicit root supplied by the caller;
    # environment-driven stage selection happens before this function is called.
    assert paths.package_version_path(Path("/repo"), "usd", "26.05") == Path("/repo/usd/26.05")
