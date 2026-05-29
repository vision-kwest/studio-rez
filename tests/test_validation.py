import pytest

from studio_rez.validation import (
    ValidationError,
    validate_package_layout,
    validate_package_name,
    validate_required_fields,
    validate_version,
)


def test_validate_package_name_accepts_studio_format():
    assert validate_package_name("usd_tools_2") == "usd_tools_2"


@pytest.mark.parametrize("name", ["Usd", "usd-tools", "usd tools", ""])
def test_validate_package_name_rejects_invalid_values(name):
    with pytest.raises(ValidationError):
        validate_package_name(name)


@pytest.mark.parametrize("version", ["1.0.0", "26.05", "1.2.3-beta.1", "1.0.0+build.5"])
def test_validate_version_accepts_expected_values(version):
    assert validate_version(version) == version


@pytest.mark.parametrize("version", ["v1.0", "", "1..2", "one"])
def test_validate_version_rejects_invalid_values(version):
    with pytest.raises(ValidationError):
        validate_version(version)


def test_validate_required_fields(tmp_path):
    package_py = tmp_path / "package.py"
    package_py.write_text(
        'name = "hello_world"\nversion = "1.0.0"\n\ndef commands():\n    pass\n',
        encoding="utf-8",
    )
    assert validate_required_fields(package_py)["name"] == "hello_world"


def test_validate_package_layout_rejects_missing_package_py(tmp_path):
    with pytest.raises(ValidationError):
        validate_package_layout(tmp_path)
