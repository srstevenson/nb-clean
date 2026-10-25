# Contributing

Search existing issues before reporting a bug or proposing a feature. Include
what you ran, what you expected, the actual result, and a small notebook that
reproduces the problem. Report security vulnerabilities privately to the
maintainer.

Discuss substantial changes in an issue before implementing them. Keep changes
small enough to review, and add tests for behaviour that could regress.

## Development

Install Rust 1.85 or later and Git, then clone the repository and create a
branch. Run `make` to list the available targets. `make fmt`, `make lint`,
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

Update documentation when commands or behaviour change. Pull requests should
describe the problem, the resulting behaviour, and the checks run. For
performance changes, include the workload and measurements.

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
