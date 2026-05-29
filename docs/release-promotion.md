# Release promotion

The studio package repositories are staged:

1. `dev` receives new CI builds.
2. `test` receives immutable packages that passed initial validation.
3. `prod` receives approved packages for artists, render nodes, and production jobs.
4. `archive` stores packages removed from active use.

Promotion copies an installed package version directory from one stage to another:

```bash
studio-rez-promote-package usd 26.05 dev test
studio-rez-promote-package usd 26.05 test prod --dry-run
studio-rez-promote-package usd 26.05 test prod
```

The current tool refuses to overwrite existing destination packages. This protects production from accidental rebuilds with the same version number.
