import os
import subprocess


BOOTSTRAP = "scripts/studio-rez-bootstrap-core-packages"


def write_fake_rez_bind(bin_dir):
    rez_bind = bin_dir / "rez-bind"
    rez_bind.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 3 || \"$1\" != \"--install-path\" ]]; then
  echo \"unexpected rez-bind arguments: $*\" >&2
  exit 64
fi
install_path=\"$2\"
package=\"$3\"
case \"$package\" in
  platform) variant=linux ;;
  arch) variant=x86_64 ;;
  os) variant=Ubuntu-24.04 ;;
  *) echo \"unexpected package: $package\" >&2; exit 65 ;;
esac
mkdir -p \"$install_path/$package/$variant\"
printf 'name = \"%s\"\\n' \"$package\" > \"$install_path/$package/$variant/package.py\"
""",
        encoding="utf-8",
    )
    rez_bind.chmod(0o755)


def bootstrap_env(tmp_path, bin_dir):
    rez_config = tmp_path / "rezconfig.py"
    rez_config.write_text("packages_path = []\n", encoding="utf-8")
    package_root = tmp_path / "packages"
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["STUDIO_REZ_ROOT"] = os.getcwd()
    env["STUDIO_PACKAGE_ROOT"] = str(package_root)
    env["STUDIO_PACKAGE_DEV"] = str(package_root / "dev")
    env["STUDIO_PACKAGE_TEST"] = str(package_root / "test")
    env["STUDIO_PACKAGE_PROD"] = str(package_root / "prod")
    env["REZ_CONFIG_FILE"] = str(rez_config)
    env["REZ_PACKAGES_PATH"] = str(package_root / "dev")
    return env, package_root


def run_bootstrap(env, *args):
    return subprocess.run(
        [BOOTSTRAP, *args],
        check=False,
        cwd=os.getcwd(),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_bootstrap_core_packages_uses_install_path_before_package(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_fake_rez_bind(bin_dir)
    env, package_root = bootstrap_env(tmp_path, bin_dir)

    result = run_bootstrap(env, "--stage", "dev")

    assert result.returncode == 0, result.stdout + result.stderr
    assert (package_root / "dev" / "platform" / "linux" / "package.py").is_file()
    assert (package_root / "dev" / "arch" / "x86_64" / "package.py").is_file()
    assert (package_root / "dev" / "os" / "Ubuntu-24.04" / "package.py").is_file()
    assert "rez-bind --install-path" in result.stdout


def test_bootstrap_core_packages_is_idempotent_and_warns(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_fake_rez_bind(bin_dir)
    env, package_root = bootstrap_env(tmp_path, bin_dir)

    first = run_bootstrap(env, "--stage", "dev")
    second = run_bootstrap(env, "--stage", "dev")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert "WARN: existing Rez implicit package(s) for platform" in second.stderr
    assert str(package_root / "dev" / "platform" / "linux" / "package.py") in second.stderr
