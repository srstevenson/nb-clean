# Contributing

Search existing issues before reporting a bug or proposing a feature. Include
what you ran, what you expected, the actual result, and a small notebook that
reproduces the problem. Report security vulnerabilities privately to the
maintainer.

Discuss substantial changes in an issue before implementing them. Keep changes
small enough to review, and add tests for behaviour that could regress.

## Development

Install Rust 1.85 or later and Git, then clone the repository and create a branch.
The optional `just` recipes run the same commands below:

```sh
cargo fmt --check
cargo clippy --all-targets --locked -- -D warnings
cargo test --locked
cargo build --release --locked
```

Use `cargo fmt` to format changes. Tests exercise notebook cleaning, the CLI,
and real Git repositories, including linked worktrees. Keep notebook fixtures
small and give each one a clear purpose.

Update documentation when commands or behaviour change. Pull requests should
describe the problem, the resulting behaviour, and the checks run. For
performance changes, include the workload and measurements.

## Releases

Maintainer setup and publishing instructions are in [Releasing](RELEASING.md).
