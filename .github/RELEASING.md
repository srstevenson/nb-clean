# Releasing

nb-clean is distributed through crates.io, PyPI wheels, and GitHub binary
archives. Publishing requires maintainer access to these services.

## Initial setup

Before the first PyPI release, configure these settings:

1. Create the `pypi` environment in the GitHub repository settings. Restrict it
   to `v*` tags and require maintainer approval for publishing.
2. In the existing `nb-clean` project's PyPI publishing settings, add a GitHub
   trusted publisher with owner `srstevenson`, repository `nb-clean`, workflow
   filename `release.yml`, and environment `pypi`.
3. Protect the release tags against unauthorised creation or modification.

GitHub environment protection and the PyPI trusted publisher are account
settings; committing the workflow does not configure them. PyPI uses
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no PyPI API
token is needed. Configure crates.io credentials separately for manual crate
publication.

## Distribution builds

The release workflow tests and builds five native targets: Linux and macOS on
ARM64 and x86-64, and Windows on x86-64. It attaches binary archives and
checksums to a draft GitHub release. Linux archives use glibc and are built on
Ubuntu 22.04.

The shared wheel workflow builds and tests one wheel per platform, used by all
supported Python versions. Linux wheels use manylinux2014 (glibc 2.17 or later),
built in pinned PyPA containers. Only wheels are published to PyPI; platforms
without a compatible wheel can use Cargo or standalone archives.

After the archive builds, wheel checks, and draft release succeed, the `pypi`
job can publish the tested wheels without rebuilding. It runs in the `pypi`
GitHub environment and has permission to request an identity token. Build jobs
have read-only permissions and cannot request that token.

## Release procedure

1. Update the version in `Cargo.toml` and `Cargo.lock`, and update the pre-commit
   example in the README.
2. Run the [development checks](CONTRIBUTING.md#development) and
   `cargo publish --dry-run --locked`. Build and test a local wheel using the
   [wheel instructions](CONTRIBUTING.md#local-python-wheels), and confirm GitHub
   CI passes on all supported platforms.
3. After review, tag the release as `vVERSION` and push the tag to trigger the
   release workflow.
4. Inspect the build results and draft assets, then approve the `pypi` job to
   publish the wheels.
5. Publish the crate with `cargo publish --locked` using the maintainer's
   crates.io credentials, and publish the draft GitHub release after reviewing
   its assets.

PyPI publication, crate publication, and publishing the draft GitHub release
are separate actions.
