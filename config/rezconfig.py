"""Conservative shared Rez configuration for studio production resolves."""

# Production is the default package repository because regular artist and
# render-farm resolves should only see promoted, validated packages.
packages_path = ["/opt/studio/packages/prod"]

# New packages are released into dev first. Promotion tooling copies immutable
# package versions from dev to test and then to prod after validation.
release_packages_path = "/opt/studio/packages/dev"

# Rez's standard implicit packages capture host platform details in resolves.
# Keeping these implicit avoids manually adding platform/arch/os requirements to
# every package.py file.
implicit_packages = ["platform", "arch", "os"]

# No global package filter by default; package visibility is controlled by the
# configured stage-specific repository paths.
package_filter = None

# Some third-party or legacy Rez packages may not carry timestamps. Do not warn
# globally; validation and promotion policies should enforce studio standards.
warn_untimestamped = False

# Temporary resolve/build directories should be removed unless a command opts in
# to preserving them for debugging.
keep_tmpdirs = False
