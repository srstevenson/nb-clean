# Releasing

Update the version in `Cargo.toml` and `Cargo.lock`, update the pre-commit example
in the README, and run the [development checks](CONTRIBUTING.md#development) and `cargo publish --dry-run --locked`.

After review, tag the release as `vVERSION`. The release workflow tests and builds
five native targets and attaches archives and checksums to a draft GitHub release.
Linux archives use glibc and are built on Ubuntu 22.04. Inspect the workflow
results and draft assets before publishing the GitHub release.

Publish the crate with `cargo publish --locked` using the maintainer's crates.io
credentials. Publishing and pushing release tags are separate maintainer actions.
PyPI publishing is not yet configured.

Wheel builds are a local prototype. Linux and Windows wheel validation, the
manylinux baseline, and PyPI publishing are still to be configured. The GitHub
release workflow currently builds standalone archives only.
