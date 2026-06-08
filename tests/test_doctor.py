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


def load_doctor_module(monkeypatch):
    import importlib.machinery
    import importlib.util

    python_dir = os.path.join(os.getcwd(), "python")
    monkeypatch.syspath_prepend(python_dir)
    loader = importlib.machinery.SourceFileLoader("studio_rez_doctor", DOCTOR)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_rez_missing_warns_in_soft_mode_without_pass(monkeypatch, capsys):
    doctor = load_doctor_module(monkeypatch)
    monkeypatch.setattr(doctor.shutil, "which", lambda _command: None)
    monkeypatch.setattr(doctor, "can_import_rez", lambda: False)

    checks = doctor.check_rez_dependencies(soft=True)

    output = capsys.readouterr().out
    assert checks == [True, True, True]
    assert "[WARN] rez command availability: not found on PATH" in output
    assert "[WARN] rez-env command availability: not found on PATH" in output
    assert "[WARN] Rez Python import availability: not importable" in output
    assert "[PASS] rez command availability" not in output
    assert "[PASS] rez-env command availability" not in output
    assert "[PASS] Rez Python import availability" not in output
    assert "python3 -m venv /opt/studio/rez/venv" in output
    assert "source /opt/studio/rez/venv/bin/activate" in output
    assert "pip install rez" in output
    assert "export PATH=/opt/studio/rez/venv/bin:$PATH" in output


def test_rez_missing_fails_in_normal_mode_without_pass(monkeypatch, capsys):
    doctor = load_doctor_module(monkeypatch)
    monkeypatch.setattr(doctor.shutil, "which", lambda _command: None)
    monkeypatch.setattr(doctor, "can_import_rez", lambda: False)

    checks = doctor.check_rez_dependencies(soft=False)

    output = capsys.readouterr().out
    assert checks == [False, False, False]
    assert "[FAIL] rez command availability: not found on PATH" in output
    assert "[FAIL] rez-env command availability: not found on PATH" in output
    assert "[FAIL] Rez Python import availability: not importable" in output
    assert "[PASS] rez command availability" not in output
    assert "[PASS] rez-env command availability" not in output
    assert "[PASS] Rez Python import availability" not in output
    assert "python3 -m venv /opt/studio/rez/venv" in output
