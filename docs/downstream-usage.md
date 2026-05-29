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
