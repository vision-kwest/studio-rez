# Reference-based Rez promotion (Issue #6)

The original `studio-rez-promote-package` copy-based command is unchanged.
The opt-in `studio-rez-promote-link` command stores a package once under
`artifacts/<name>/<version>/<build_id>` and creates create-only relative
symlinks under the selected stage. The publisher must have write permission;
workstations need only read access.

```bash
export STUDIO_PACKAGE_ROOT=/opt/studio/packages
studio-rez-promote-link publish usd 26.05 build_001
studio-rez-promote-link link usd 26.05 build_001 --stage test
# After approval:
studio-rez-promote-link link usd 26.05 build_001 --stage prod
```

Existing `test/usd/26.05` and `prod/usd/26.05` directories are never
overwritten. To adopt links for an already published version, migrate in
a separately approved maintenance window; do not delete or replace those
directories with this command.

Artifact publication copies the source dev package once to a unique build ID,
rejects external source symlinks, creates a per-build exclusive lock, and removes
ordinary filesystem write bits from the published tree. A stage link is created
atomically and refuses overwrite. A different artifact ID is required for
each new build.

**Important limitations:** Read-only POSIX mode is not a security boundary
against a privileged publisher or filesystem administrator. Enforce publisher
permissions separately and never modify or delete referenced artifacts.
No automatic rollback, stage replacement, checksum attestation or garbage
collection is provided. Stale `.publishing` locks require operator inspection;
do not remove them while another publisher is active.

Validated against Rez 3.4.0 and a disposable package on real EFS, including
a live `rez-env` execution. Real OpenUSD 26.05 symlink resolution/execution
was separately verified from a read-only EFS mount. The existing copied
production packages remain untouched.
