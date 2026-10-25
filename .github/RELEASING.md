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

Replace `VERSION` below with the release version, such as `5.0.0`.

1. Update the version in `Cargo.toml` and `Cargo.lock`, and update the
   pre-commit example in the README. Commit these changes. Run the
   [development checks](CONTRIBUTING.md#development), and build and test a local
   wheel using the [wheel instructions](CONTRIBUTING.md#local-python-wheels).
2. Once CI passes on all supported platforms, approve and merge the pull
   request into `main`. Update your local checkout:

   ```sh
   git switch main
   git pull --ff-only
   ```

3. Confirm the merged commit passes CI, its version matches the intended
   release, and there are no uncommitted package changes. Run the publishing
   checks without uploading:

   ```sh
   cargo publish --dry-run --locked
   ```

4. Tag that commit and push the tag to start the release workflow:

   ```sh
   git tag -a vVERSION -m "Release nb-clean VERSION"
   git push origin vVERSION
   ```

5. Wait for the release workflow to build and test the binaries and wheels.
   It creates a draft GitHub release and waits for approval of the `pypi`
   environment.
6. Inspect the workflow results, draft release assets, checksums, and generated
   release notes. Edit the notes as needed. Approve the `pypi` job, then confirm
   publication to PyPI succeeds.
7. Publish to crates.io from the same tagged source, using the maintainer's
   crates.io credentials. Confirm there are no uncommitted package changes:

   ```sh
   git switch --detach vVERSION
   cargo publish --locked
   ```

8. Publish the draft GitHub release once PyPI and crates.io publication have
   succeeded.

Merging the pull request does not publish a release. Pushing the tag starts
release preparation; approving the `pypi` job authorises the PyPI upload.
Crate publication and publication of the draft GitHub release are manual steps.
