.DEFAULT_GOAL := help

.PHONY: all
all: fmt lint test

.PHONY: install
install:
	uv sync

.PHONY: fmt
fmt:
	uv run ruff format

.PHONY: lint
lint:
	uv run ruff check --fix
	uv run ty check

.PHONY: check
check:
	uv run ruff format --check
	uv run ruff check
	uv run ty check

.PHONY: test
test:
	uv run coverage run -m pytest
	uv run coverage report

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make help     - Show this help message (default)"
	@echo "  make all      - Format (ruff), lint (ruff, ty), and test (pytest)"
	@echo "  make install  - Install dependencies with uv"
	@echo "  make fmt      - Format code with ruff"
	@echo "  make lint     - Lint with ruff (--fix) and type-check with ty"
	@echo "  make check    - Check formatting (ruff), lint (ruff), and types (ty)"
	@echo "  make test     - Run tests with pytest and report coverage"
