"""Test fixtures."""

import pathlib
from typing import cast

import nbformat
import pytest

NOTEBOOKS_DIR = pathlib.Path(__file__).parent / "notebooks"


def read_notebook(filename: str) -> nbformat.NotebookNode:
    """Read a test notebook from the file system.

    Parameters
    ----------
    filename : str
        Filename of the notebook.

    Returns
    -------
    nbformat.NotebookNode
        The notebook.

    """
    return cast(
        nbformat.NotebookNode,
        nbformat.read(NOTEBOOKS_DIR / filename, as_version=nbformat.NO_CONVERT),  # type: ignore[no-untyped-call]
    )


@pytest.fixture()
def dirty_notebook() -> nbformat.NotebookNode:
    """Return a dirty notebook."""
    return read_notebook("dirty.ipynb")


@pytest.fixture()
def dirty_notebook_with_version() -> nbformat.NotebookNode:
    """Return a dirty notebook containing the Python version."""
    return read_notebook("dirty_with_version.ipynb")


@pytest.fixture()
def clean_notebook() -> nbformat.NotebookNode:
    """Return a clean notebook."""
    return read_notebook("clean.ipynb")


@pytest.fixture()
def clean_notebook_with_notebook_metadata() -> nbformat.NotebookNode:
    """Return a clean notebook with notebook metadata."""
    return read_notebook("clean_with_notebook_metadata.ipynb")


@pytest.fixture()
def clean_notebook_without_empty_cells() -> nbformat.NotebookNode:
    """Return a clean notebook without empty cells."""
    return read_notebook("clean_without_empty_cells.ipynb")


@pytest.fixture()
def clean_notebook_with_empty_cells() -> nbformat.NotebookNode:
    """Return a clean notebook containing empty cells."""
    return read_notebook("clean_with_empty_cells.ipynb")


@pytest.fixture()
def clean_notebook_with_counts() -> nbformat.NotebookNode:
    """Return a clean notebook with only input cell execution counts."""
    return read_notebook("clean_with_counts.ipynb")


@pytest.fixture()
def clean_notebook_with_cell_metadata() -> nbformat.NotebookNode:
    """Return a clean notebook with cell metadata."""
    return read_notebook("clean_with_cell_metadata.ipynb")


@pytest.fixture()
def clean_notebook_with_tags_metadata() -> nbformat.NotebookNode:
    """Return a clean notebook with only `tags` cell metadata."""
    return read_notebook("clean_with_tags_metadata.ipynb")


@pytest.fixture()
def clean_notebook_with_tags_special_metadata() -> nbformat.NotebookNode:
    """Return a clean notebook with only `tags` and `special` cell metadata."""
    return read_notebook("clean_with_tags_special_metadata.ipynb")


@pytest.fixture()
def clean_notebook_with_outputs() -> nbformat.NotebookNode:
    """Return a clean notebook with cell outputs."""
    return read_notebook("clean_with_outputs.ipynb")


@pytest.fixture()
def clean_notebook_with_outputs_with_counts() -> nbformat.NotebookNode:
    """Return a notebook with cell outputs and output execution counts."""
    return read_notebook("clean_with_outputs_with_counts.ipynb")
