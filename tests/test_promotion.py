from pathlib import Path

from studio_rez.promotion import promote_package


def test_promotion_uses_monkeypatched_package_root(monkeypatch, tmp_path):
    package_root = tmp_path / "packages"
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(package_root))
    monkeypatch.setenv("STUDIO_PACKAGE_DEV", "/opt/studio/packages/dev")
    monkeypatch.setenv("STUDIO_PACKAGE_TEST", "/opt/studio/packages/test")

    source_package = package_root / "dev" / "usd" / "26.05"
    source_package.mkdir(parents=True)
    (source_package / "package.py").write_text('name = "usd"\nversion = "26.05"\n', encoding="utf-8")

    result = promote_package("usd", "26.05", "dev", "test")

    expected_destination = package_root / "test" / "usd" / "26.05"
    assert Path(result["source"]) == source_package
    assert Path(result["destination"]) == expected_destination
    assert expected_destination.is_dir()
    assert "/opt/studio/packages" not in result["source"]
    assert "/opt/studio/packages" not in result["destination"]


def test_reference_promotion_keeps_cli_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(tmp_path))
    source = tmp_path / "dev/usd/26.05"
    source.mkdir(parents=True)
    (source / "package.py").write_text('name="usd"\nversion="26.05"\n')
    (source / "payload").write_text("unchanged")
    assert promote_package("usd", "26.05", "dev", "test", dry_run=True)["dry_run"]
    assert source.is_dir() and not source.is_symlink()
    promote_package("usd", "26.05", "dev", "test")
    promote_package("usd", "26.05", "test", "prod")
    artifact = tmp_path / "artifacts/usd/26.05/published"
    assert artifact.is_dir()
    for stage in ("dev", "test", "prod"):
        link = tmp_path / stage / "usd/26.05"
        assert link.is_symlink()
        assert link.resolve() == artifact
        assert (link / "payload").read_text() == "unchanged"
    with __import__("pytest").raises(FileExistsError):
        promote_package("usd", "26.05", "test", "prod")


def test_rejects_broken_destination_link(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_PACKAGE_ROOT", str(tmp_path))
    source = tmp_path / "dev/usd/26.05"
    source.mkdir(parents=True)
    (source / "package.py").write_text('name="usd"\n')
    dest = tmp_path / "test/usd/26.05"
    dest.parent.mkdir(parents=True)
    dest.symlink_to("missing")
    with __import__("pytest").raises(FileExistsError):
        promote_package("usd", "26.05", "dev", "test")
