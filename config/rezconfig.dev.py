"""Rez configuration for development and CI package builds."""

# Development resolves prefer newly built dev packages, then test candidates,
# then production fallbacks.
packages_path = [
    "/opt/studio/packages/dev",
    "/opt/studio/packages/test",
    "/opt/studio/packages/prod",
]

# rez-build --install releases into dev by default.
release_packages_path = "/opt/studio/packages/dev"

implicit_packages = ["platform", "arch", "os"]
package_filter = None
warn_untimestamped = False
keep_tmpdirs = False
