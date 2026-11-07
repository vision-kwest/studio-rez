# Rez reference-based promotion (default)

The existing CLI commands are unchanged:

```bash
studio-rez-promote-package usd 26.05 dev test
studio-rez-promote-package usd 26.05 test prod
```

Promotion no longer copies package payloads. When a new physical
`dev/<name>/<version>` package is first promoted, it is renamed on the
same filesystem to `artifacts/<name>/<version>/published`, and `dev`
becomes a relative symlink to the artifact. Subsequent `test` and `prod`
promotions create relative symlinks to that same artifact. Existing destination
versions are never overwritten; `--dry-run` makes no changes.

The OpenUSD `scripts/promote_usd.py` command retains its existing arguments
and delegates to `studio-rez-promote-package`. The publisher environment
must expose that command on PATH and the `studio_rez` Python package.

Workstations continue using `/opt/studio/packages/prod` as their
`REZ_PACKAGES_PATH`; EFS remains mounted at the same path. The artifact
directory must be readable through the workstation's read-only EFS mount.

Existing package directories are **not** silently migrated or overwritten.
The one-time OpenUSD 26.05 migration was completed separately on EFS using
the original production-approved payload as the canonical artifact.

Do not modify or delete artifacts referenced by any stage. The reference
workflow is single-publisher and does not provide content attestation,
automated garbage collection, or a version-replacement mechanism. For
an already-published version, a new build must use a new version or a
separately reviewed migration.
