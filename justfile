# show this help message (default)
help:
    @just -l

# format with ruff
fmt:
    uv run ruff check --fix
    uv run ruff format

# lint with ruff and type-check with ty
lint:
    uv run ruff check
    uv run ruff format --check
    uv run ty check

# run tests with pytest and report coverage
test:
    uv run coverage run -m pytest
    uv run coverage report
