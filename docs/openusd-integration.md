# OpenUSD integration

The intended OpenUSD pipeline is split across three repositories.

## `studio-ci-images`

`studio-ci-images` builds Docker images and publishes them to GHCR. For OpenUSD, it owns an image such as:

```text
ghcr.io/YOUR_ORG/openusd-builder:latest
```

That image contains compilers, CMake, Python, and third-party build dependencies needed to compile Pixar OpenUSD.

## `studio-openusd`

`studio-openusd` is the downstream package repository for OpenUSD. It pulls the `openusd-builder` image, clones Pixar OpenUSD, compiles it, and wraps the resulting install tree as a Rez package such as `usd-26.05`.

The package `commands()` should expose OpenUSD binaries, libraries, Python modules, and plugins through Rez's rex API.

## `studio-rez`

`studio-rez` supplies the shared rules: Rez config, environment setup, validation, package templates, and promotion helpers. It does not build OpenUSD itself; it standardizes how `studio-openusd` and other package repositories build and publish Rez packages.
