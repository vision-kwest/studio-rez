import os
import subprocess
import sys


DOCTOR = "scripts/studio-rez-doctor"


def doctor_env(tmp_path, package_root):
    # The doctor runs as a subprocess so the test exercises the real CLI entry
    # point and import behavior, not just helper functions in-process.
    rez_config = tmp_path / "rezconfig.py"
    rez_config.write_text("packages_path = []\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}/python{os.pathsep}{env.get('PYTHONPATH', '')}"
    env["STUDIO_PACKAGE_ROOT"] = str(package_root)
    env["REZ_CONFIG_FILE"] = str(rez_config)
    env["REZ_PACKAGES_PATH"] = str(package_root / "dev")

    # Remove stage-specific values to model the intended runtime contract: the
    # doctor should print stage paths derived from STUDIO_PACKAGE_ROOT. Other path
    # tests cover stale stage-specific values explicitly.
    env.pop("STUDIO_PACKAGE_DEV", None)
    env.pop("STUDIO_PACKAGE_TEST", None)
    env.pop("STUDIO_PACKAGE_PROD", None)
    env.pop("STUDIO_PACKAGE_ARCHIVE", None)
    return env


def run_doctor(tmp_path, package_root, *args):
    # Capture stdout/stderr so assertions can verify that human-facing diagnostic
    # text stays consistent as the implementation evolves.
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
    # --soft is meant for bootstrap/CI environments where package repositories
    # may not exist yet. Missing roots should be visible warnings, not failures.
    package_root = tmp_path / "missing-packages"

    result = run_doctor(tmp_path, package_root, "--soft")

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"[INFO] STUDIO_PACKAGE_ROOT: {package_root}" in result.stdout
    assert f"[INFO] dev root resolved: {package_root / 'dev'}" in result.stdout
    assert f"[WARN] dev root missing: {package_root / 'dev'}" in result.stdout


def test_doctor_output_is_not_contradictory_for_missing_roots(tmp_path):
    # The original EC2 report was confusing because output could imply a root
    # existed and then say writability was skipped because it was missing. Keep a
    # focused assertion on that contradiction so it cannot reappear silently.
    package_root = tmp_path / "missing-packages"

    result = run_doctor(tmp_path, package_root, "--soft")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "root writable: skipped because directory is missing" not in result.stdout
    assert "[PASS] dev root exists" not in result.stdout
    assert "[WARN] dev root missing" in result.stdout
