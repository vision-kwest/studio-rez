"""Rez configuration for production-only resolves."""

# Production resolves intentionally see only promoted packages.
packages_path = ["/opt/studio/packages/prod"]

# Keep the release target as dev to avoid accidental direct writes into prod.
release_packages_path = "/opt/studio/packages/dev"

implicit_packages = ["platform", "arch", "os"]
package_filter = None
warn_untimestamped = False
keep_tmpdirs = False
