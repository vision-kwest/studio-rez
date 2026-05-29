# studio-rez

`studio-rez` is the shared Rez standards repository for a small VFX/animation studio pipeline. It defines the Rez configuration, package repository layout, environment bootstrap scripts, package templates, validation helpers, promotion helpers, examples, and CI workflow templates used by downstream package repositories.

Rez environments resolve against centrally installed package versions. They do not copy every package into each environment; instead, a resolved environment references packages from configured package repositories such as `/opt/studio/packages/prod`.

## Repository responsibilities

| Repository | Responsibility |
| --- | --- |
| `studio-ci-images` | Builds and publishes Docker images to GHCR, such as an `openusd-builder` image with compilers and build dependencies. |
| `studio-openusd` | A downstream package repository. It pulls the builder image, compiles Pixar OpenUSD, and installs the result as a Rez package such as `usd-26.05`. |
| `studio-rez` | Provides shared Rez config, conventions, templates, validation, promotion tooling, and CI snippets used by package repositories. |

## Package repository layout

The studio package root is expected to be an Amazon EFS mount at:

```bash
/opt/studio/packages
```

Stages are separated by repository path:

```text
/opt/studio/packages/dev
/opt/studio/packages/test
/opt/studio/packages/prod
/opt/studio/packages/archive
```

## Source the environment

For day-to-day production resolves:

```bash
source /path/to/studio-rez/env/studio.sh
```

For development builds and CI installs into `dev`:

```bash
source /path/to/studio-rez/env/studio-dev.sh
```

For locked production-only resolves:

```bash
source /path/to/studio-rez/env/studio-prod.sh
```

Each script exports `STUDIO_REZ_ROOT`, package root variables, `REZ_CONFIG_FILE`, `REZ_PACKAGES_PATH`, and adds this repo's `scripts` and `python` directories to the current shell.

## Validate a package repository

```bash
source /path/to/studio-rez/env/studio-dev.sh
studio-rez-doctor --soft
studio-rez-validate-package /path/to/studio-openusd
```

The validator checks that `package.py` exists, contains `name`, `version`, and `commands`, uses an accepted package name and version format, and has no spaces in its path.

## Use from GitHub Actions

Downstream repositories can copy `templates/github-actions-build-rez-package.yml.template` into `.github/workflows/build.yml`. The workflow checks out both the downstream repo and `studio-rez`, sources `env/studio-dev.sh`, runs validation, and installs the Rez package into `/opt/studio/packages/dev`:

```yaml
- name: Source studio Rez environment and validate
  run: |
    source studio-rez/env/studio-dev.sh
    studio-rez-doctor --soft
    studio-rez-validate-package .
```

## Example downstream flow for `studio-openusd`

1. Run inside a GHCR builder image from `studio-ci-images`.
2. Check out `studio-openusd`.
3. Check out `studio-rez` beside it.
4. Source `studio-rez/env/studio-dev.sh`.
5. Compile OpenUSD.
6. Wrap the install tree with a Rez `package.py`.
7. Run `rez-build --install --prefix /opt/studio/packages/dev`.
8. Promote the immutable package directory from `dev` to `test`, then from `test` to `prod` after validation.

See `docs/downstream-usage.md` and `docs/openusd-integration.md` for details.
