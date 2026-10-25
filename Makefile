.PHONY: help
help:
	@echo "Available targets:"
	@echo "  help   show this help message"
	@echo "  fmt    format Rust code"
	@echo "  lint   check formatting and lint Rust code"
	@echo "  test   run unit and integration tests"
	@echo "  build  build the release binary"

.PHONY: fmt
fmt:
	cargo fmt

.PHONY: lint
lint:
	cargo fmt --check
	cargo clippy --all-targets --locked -- -D warnings

.PHONY: test
test:
	cargo test --locked

.PHONY: build
build:
	cargo build --release --locked
