from pathlib import Path
from typing import Final, cast

import nbformat
import pytest

NOTEBOOKS_DIR: Final = Path(__file__).parent / "notebooks"


def _read_notebook(filename: str) -> nbformat.NotebookNode:
    return cast(
        nbformat.NotebookNode,
        nbformat.read(NOTEBOOKS_DIR / filename, as_version=nbformat.NO_CONVERT),  # pyright: ignore[reportUnknownMemberType]
    )


@pytest.fixture
def dirty_notebook() -> nbformat.NotebookNode:
    return _read_notebook("dirty.ipynb")


@pytest.fixture
def dirty_notebook_with_version() -> nbformat.NotebookNode:
    return _read_notebook("dirty_with_version.ipynb")


@pytest.fixture
def clean_notebook() -> nbformat.NotebookNode:
    return _read_notebook("clean.ipynb")


@pytest.fixture
def clean_notebook_with_notebook_metadata() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_notebook_metadata.ipynb")


@pytest.fixture
def clean_notebook_without_empty_cells() -> nbformat.NotebookNode:
    return _read_notebook("clean_without_empty_cells.ipynb")


@pytest.fixture
def clean_notebook_with_empty_cells() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_empty_cells.ipynb")


@pytest.fixture
def clean_notebook_with_counts() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_counts.ipynb")


@pytest.fixture
def clean_notebook_with_cell_metadata() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_cell_metadata.ipynb")


@pytest.fixture
def clean_notebook_with_tags_metadata() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_tags_metadata.ipynb")


@pytest.fixture
def clean_notebook_with_tags_special_metadata() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_tags_special_metadata.ipynb")


@pytest.fixture
def clean_notebook_with_outputs() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_outputs.ipynb")


@pytest.fixture
def clean_notebook_with_outputs_with_counts() -> nbformat.NotebookNode:
    return _read_notebook("clean_with_outputs_with_counts.ipynb")


@pytest.fixture
def clean_notebook_without_notebook_metadata() -> nbformat.NotebookNode:
    return _read_notebook("clean_without_notebook_metadata.ipynb")
