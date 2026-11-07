"""Focused offline tests for the opt-in Issue #6 prototype."""
import pytest

from studio_rez.reference_promotion import publish_artifact, promote_link


def test_publish_and_link_without_duplicate_payload(tmp_path):
    source = tmp_path / "dev/usd/26.05"
    (source / "bin").mkdir(parents=True)
    (source / "package.py").write_text('name = "usd"\nversion = "26.05"\n')
    (source / "bin/usdcat").write_text("v1")
    artifact = publish_artifact("usd", "26.05", "build_001", tmp_path)
    test = promote_link("usd", "26.05", "build_001", "test", tmp_path)
    prod = promote_link("usd", "26.05", "build_001", "prod", tmp_path)
    assert test.is_symlink() and prod.is_symlink()
    assert test.resolve() == artifact == prod.resolve()
    assert (prod / "bin/usdcat").read_text() == "v1"
    (source / "bin/usdcat").write_text("v2")
    assert (prod / "bin/usdcat").read_text() == "v1"
    with pytest.raises(FileExistsError):
        promote_link("usd", "26.05", "build_001", "prod", tmp_path)
    with pytest.raises(FileExistsError):
        publish_artifact("usd", "26.05", "build_001", tmp_path)


def test_missing_artifact_and_invalid_stage(tmp_path):
    with pytest.raises(FileNotFoundError):
        promote_link("usd", "26.05", "missing", "test", tmp_path)
    with pytest.raises(ValueError):
        promote_link("usd", "26.05", "missing", "dev", tmp_path)
