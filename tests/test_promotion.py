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
