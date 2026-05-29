# Repository layout

`studio-rez` is intentionally small and copy-paste friendly.

```text
env/         Shell bootstrap scripts for dev/prod Rez configuration.
config/      Rez configuration files selected with REZ_CONFIG_FILE.
python/      Python helper modules used by CLIs and tests.
scripts/     Executable CLIs for validation, doctor checks, promotion, and skeleton creation.
templates/   Package and GitHub Actions templates for downstream repos.
docs/        Human documentation for package authors and release managers.
examples/    Minimal packages that demonstrate Rez commands and dependencies.
tests/       Pytest coverage for core helpers.
```

Downstream package repositories should not copy helper code directly. They should check out `studio-rez` in CI and source the appropriate environment script.
