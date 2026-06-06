import os
import subprocess
import sys


DOCTOR = "scripts/studio-rez-doctor"


def doctor_env(tmp_path, package_root):
    rez_config = tmp_path / "rezconfig.py"
    rez_config.write_text("packages_path = []\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}/python{os.pathsep}{env.get('PYTHONPATH', '')}"
    env["STUDIO_PACKAGE_ROOT"] = str(package_root)
    env["REZ_CONFIG_FILE"] = str(rez_config)
    env["REZ_PACKAGES_PATH"] = str(package_root / "dev")
    env.pop("STUDIO_PACKAGE_DEV", None)
    env.pop("STUDIO_PACKAGE_TEST", None)
    env.pop("STUDIO_PACKAGE_PROD", None)
    env.pop("STUDIO_PACKAGE_ARCHIVE", None)
    return env


def run_doctor(tmp_path, package_root, *args):
    return subprocess.run(
        [sys.executable, DOCTOR, *args],
        check=False,
        cwd=os.getcwd(),
        env=doctor_env(tmp_path, package_root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_doctor_soft_does_not_fail_when_package_root_is_missing(tmp_path):
    package_root = tmp_path / "missing-packages"

    result = run_doctor(tmp_path, package_root, "--soft")

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"[INFO] STUDIO_PACKAGE_ROOT: {package_root}" in result.stdout
    assert f"[INFO] dev root resolved: {package_root / 'dev'}" in result.stdout
    assert f"[WARN] dev root missing: {package_root / 'dev'}" in result.stdout


def test_doctor_output_is_not_contradictory_for_missing_roots(tmp_path):
    package_root = tmp_path / "missing-packages"

    result = run_doctor(tmp_path, package_root, "--soft")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "root writable: skipped because directory is missing" not in result.stdout
    assert "[PASS] dev root exists" not in result.stdout
    assert "[WARN] dev root missing" in result.stdout
