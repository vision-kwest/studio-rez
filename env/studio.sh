#!/usr/bin/env bash
# Source this file to configure the shared studio Rez environment.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "ERROR: env/studio.sh must be sourced, not executed." >&2
  echo "Usage: source env/studio.sh" >&2
  exit 2
fi

_studio_rez_source="${BASH_SOURCE[0]}"
while [[ -L "${_studio_rez_source}" ]]; do
  _studio_rez_dir="$(cd -P "$(dirname "${_studio_rez_source}")" >/dev/null 2>&1 && pwd)"
  _studio_rez_source="$(readlink "${_studio_rez_source}")"
  [[ "${_studio_rez_source}" != /* ]] && _studio_rez_source="${_studio_rez_dir}/${_studio_rez_source}"
done
_studio_rez_env_dir="$(cd -P "$(dirname "${_studio_rez_source}")" >/dev/null 2>&1 && pwd)"
export STUDIO_REZ_ROOT="$(cd "${_studio_rez_env_dir}/.." >/dev/null 2>&1 && pwd)"

export STUDIO_PACKAGE_ROOT="/opt/studio/packages"
export STUDIO_PACKAGE_DEV="${STUDIO_PACKAGE_ROOT}/dev"
export STUDIO_PACKAGE_TEST="${STUDIO_PACKAGE_ROOT}/test"
export STUDIO_PACKAGE_PROD="${STUDIO_PACKAGE_ROOT}/prod"
export STUDIO_PACKAGE_ARCHIVE="${STUDIO_PACKAGE_ROOT}/archive"

export REZ_CONFIG_FILE="${STUDIO_REZ_ROOT}/config/rezconfig.py"
export REZ_PACKAGES_PATH="${STUDIO_PACKAGE_PROD}"

case ":${PATH}:" in
  *":${STUDIO_REZ_ROOT}/scripts:"*) ;;
  *) export PATH="${STUDIO_REZ_ROOT}/scripts:${PATH}" ;;
esac

if [[ -n "${PYTHONPATH:-}" ]]; then
  case ":${PYTHONPATH}:" in
    *":${STUDIO_REZ_ROOT}/python:"*) ;;
    *) export PYTHONPATH="${STUDIO_REZ_ROOT}/python:${PYTHONPATH}" ;;
  esac
else
  export PYTHONPATH="${STUDIO_REZ_ROOT}/python"
fi

if [[ "${STUDIO_REZ_QUIET:-0}" != "1" ]]; then
  echo "studio-rez: configured prod environment (${REZ_PACKAGES_PATH})"
fi

unset _studio_rez_source _studio_rez_dir _studio_rez_env_dir
