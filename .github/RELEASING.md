# Releasing

nb-clean is distributed through crates.io, PyPI wheels, and GitHub binary
archives. Publishing requires maintainer access to these services.

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

1. Update the version in `Cargo.toml` and `Cargo.lock`, and update the
   pre-commit example in the README. Commit these changes before running the
   publish dry run.
2. Run the [development checks](CONTRIBUTING.md#development) and
   `cargo publish --dry-run --locked`. Build and test a local wheel using the
   [wheel instructions](CONTRIBUTING.md#local-python-wheels), and confirm GitHub
   CI passes on all supported platforms.
3. After review and merging to `main`, tag the exact commit that passed CI as
   `vVERSION`. Push the tag to trigger the release workflow.
4. Inspect the build results and draft assets, then approve the `pypi` job to
   publish the wheels.
5. Check out the release tag with `git switch --detach vVERSION` and confirm
   there are no uncommitted package changes. Publish the crate with
   `cargo publish --locked` using the maintainer's crates.io credentials, and
   publish the draft GitHub release after reviewing its assets.

PyPI publication, crate publication, and publishing the draft GitHub release
are separate actions.
