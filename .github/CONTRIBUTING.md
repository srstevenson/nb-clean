# Contributing

Thanks for considering contributing! The following is a set of guidelines for
doing so. They're guidelines rather than rules, so follow your best judgement,
but reading them will help make the contribution process easier and more
effective for both you and the maintainers.

## Reporting issues

GitHub issues are used for managing bug reports and feature requests, except
security vulnerabilities: these should be emailed to the maintainers instead.

Search for existing issues before creating a new one, to ensure your problem
hasn't already been reported. If it has, you're welcome to comment on the
existing issue with extra information that might help reproduce and fix the
problem, or sharing why a feature would be useful, but refrain from "+1" type
comments. Duplicate issues will be closed with a reference to the existing
issue.

In your report describe what you did, what you expected to happen, and what
happened instead. Provide a [minimal reproducible example][mre] that the
maintainers can run. Provide as much detail as you can in your description of
the problem, including the version of the project you're using, and details of
your operating system and environment, and other information which might help
diagnose the problem, such as what you've already tried to fix it.

## Contributing changes

### Planning

When you contribute a new change, the responsibility for maintenance is (by
default) transferred to the existing project maintainers. The benefit of the
contribution must be weighed against the cost of maintaining it.

If you're considering contributing a non-trivial bugfix or feature, discuss the
changes you plan to make before you start coding by opening an issue. This
ensures your proposed change will be accepted, and provides the maintainers the
opportunity to help you.

### Implementation

Changes are managed using GitHub pull requests. If you're new to pull requests,
read the [documentation][pr docs] to learn how they work.

Install Rust 1.85 or later with rustfmt and Clippy, and install Git. Python,
[uv], Ruff, and ty are needed when working on Python wheel packaging or its
smoke test.

After cloning the repository, you can implement your changes as follows:

1. Before making your changes, run the tests with `make test`, and ensure they
   pass. This checks your development environment is correctly configured, and
   there aren't outstanding issues before you start coding. If they don't pass,
   you can open a GitHub issue for help debugging.
2. Check out a new branch for your changes, branching from `main`, with a
   sensible name for your changes.
3. Implement your changes.
4. If you introduced new functionality or fixed a bug, add appropriate automated
   tests to prevent future regressions.
5. Ensure you've updated any documentation comments or documentation files
   (including `README.md`) which are affected by your change.
6. Run the formatter and linter with `make fmt lint`, and tests with
   `make test`, and fix any problems. If you changed the wheel smoke test, also
   run `ruff format tests/test_wheel.py`, `ruff check tests/test_wheel.py`, and
   `ty check tests/test_wheel.py`.
7. Commit your changes, following [these guidelines][commit guidelines] for your
   commit messages.
8. Fork the base repository on GitHub, push your branch to your fork, and open a
   pull request against the base repository. Make sure your pull request has a
   clear title and description. The easier your changes are to understand, the
   easier it is for the maintainers to approve and merge them. For performance
   changes, include the workload and measurements.
9. Your pull request will be reviewed by the maintainers and either merged, or
   feedback will be provided on changes that are required.

## Development

Run `make` to list the available targets. `make fmt`, `make lint`,
`make test`, and `make build` provide shortcuts for formatting, checks, tests,
and release builds. You can also run the commands directly:

```sh
cargo fmt --check
cargo clippy --all-targets --locked -- -D warnings
cargo test --locked
cargo build --release --locked
```

To install the executable from your checkout:

```sh
cargo install --path . --locked
```

Use `cargo fmt` to format changes. Tests exercise notebook cleaning, the CLI,
and real Git repositories, including linked worktrees. Keep notebook fixtures
small and give each one a clear purpose.

## Local Python wheels

Install uv and Rust, then build a wheel for the current platform:

```sh
uv build --wheel
```

The wheel is written to `dist/`. Maturin packages the native executable
directly; there is no Python wrapper or runtime package dependency. The version
comes from `Cargo.toml`. Installation requires Python 3.10 or later.

Run the built wheel in an isolated environment, replacing the path below with
the wheel's filename:

```sh
uvx --no-index --from /path/to/nb_clean.whl nb-clean --version
```

For checks involving files or Git filters, install the wheel into a virtual
environment with
`uv pip install --python /path/to/venv/bin/python /path/to/nb_clean.whl` and put
that environment's scripts directory on `PATH`. On Windows, the directory is
`Scripts` instead of `bin`.

Run the same installation and CLI checks used in CI with Python 3.10 or later:

```sh
python3 tests/test_wheel.py dist
```

The directory must contain exactly one wheel for the current platform. The
script creates a temporary environment, installs the wheel without accessing
an index, and checks notebook cleaning, exit statuses, and Git staging.

CI runs these wheel checks on Linux, macOS, and Windows.

## Releases

Maintainer setup and publishing instructions are in [Releasing](RELEASING.md).

[commit guidelines]:
  <https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>
[mre]: https://stackoverflow.com/help/minimal-reproducible-example
[pr docs]: https://docs.github.com/en/github/collaborating-with-pull-requests
[uv]: https://docs.astral.sh/uv/
