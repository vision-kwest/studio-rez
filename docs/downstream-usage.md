# Downstream usage

This page describes how a package repository such as `studio-openusd` consumes `studio-rez`.

## CI checkout pattern

A downstream workflow checks out both repositories side by side:

```yaml
- name: Checkout studio-openusd
  uses: actions/checkout@v4
  with:
    path: studio-openusd

- name: Checkout studio-rez
  uses: actions/checkout@v4
  with:
    repository: YOUR_ORG/studio-rez
    path: studio-rez
```

## Source the dev environment

Build jobs install into the dev package repository:

```bash
cd studio-openusd
source ../studio-rez/env/studio-dev.sh
studio-rez-doctor --soft
studio-rez-validate-package .
```

`studio-dev.sh` sets `REZ_CONFIG_FILE` to `config/rezconfig.dev.py` and sets `REZ_PACKAGES_PATH` to dev, test, and prod in that order.


## Bootstrap implicit Rez packages

Before building downstream packages in a fresh package repository, bind Rez's implicit core packages into the target stage. For the dev stage, run:

```bash
source ../studio-rez/env/studio-dev.sh
studio-rez-bootstrap-core-packages --stage dev
```

The helper runs the Rez 3.4 command form below for each implicit package:

```bash
rez-bind --install-path /opt/studio/packages/dev platform
rez-bind --install-path /opt/studio/packages/dev arch
rez-bind --install-path /opt/studio/packages/dev os
```

The package name comes after `--install-path`; `rez-bind platform --install-path ...` and `rez-bind --path ...` are not the correct forms for this bootstrap. Existing bound packages are reported as warnings and left unchanged, so the helper can be rerun safely.

## Build OpenUSD

`studio-openusd` should run inside a builder image from `studio-ci-images`, clone Pixar OpenUSD, compile it, and stage the install tree under the package repository workspace.

## Install into Rez dev

After the build produces a valid `package.py`, install the package to the dev repository:

```bash
rez-build --install --prefix /opt/studio/packages/dev
```

Rez installs a central package version under a path like:

```text
/opt/studio/packages/dev/usd/26.05
```

Resolved environments reference that central package. They do not copy OpenUSD into each resolved environment.

## Promote later

After validation, release managers promote immutable package directories:

```bash
studio-rez-promote-package usd 26.05 dev test
studio-rez-promote-package usd 26.05 test prod
```
