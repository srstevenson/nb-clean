# show available recipes
help:
    @just -l

# format Rust code
fmt:
    cargo fmt

# check formatting and lint Rust code
lint:
    cargo fmt --check
    cargo clippy --all-targets --locked -- -D warnings

# run unit and integration tests
test:
    cargo test --locked

# build the release binary
build:
    cargo build --release --locked
