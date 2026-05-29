from studio_rez.manifests import create_build_manifest, read_manifest, write_manifest


def test_manifest_round_trip(tmp_path):
    data = create_build_manifest(
        package_name="usd",
        version="26.05",
        source_repo="https://github.com/example/studio-openusd",
        source_commit="abc123",
        build_image="ghcr.io/example/openusd-builder:latest",
        build_time="2026-05-29T00:00:00Z",
    )
    path = write_manifest(tmp_path / "manifest.json", data)
    assert read_manifest(path) == data
