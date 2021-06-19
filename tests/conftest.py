"""Test fixtures."""

import pathlib

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
    return nbformat.read(
        NOTEBOOKS_DIR / filename, as_version=nbformat.NO_CONVERT
    )


@pytest.fixture
def dirty_notebook() -> nbformat.NotebookNode:
    """A dirty notebook."""
    return read_notebook("dirty.ipynb")

@pytest.fixture
def dirty_notebook_with_version() -> nbformat.NotebookNode:
    """A dirty notebook with the python version."""
    return read_notebook("dirty_with_version.ipynb")


@pytest.fixture
def clean_notebook() -> nbformat.NotebookNode:
    """A clean notebook."""
    return read_notebook("clean.ipynb")


@pytest.fixture
def clean_notebook_with_empty_cells() -> nbformat.NotebookNode:
    """A clean notebook containing empty cells."""
    return read_notebook("clean_with_empty_cells.ipynb")


@pytest.fixture
def clean_notebook_with_metadata() -> nbformat.NotebookNode:
    """A clean notebook with cell metadata."""
    return read_notebook("clean_with_metadata.ipynb")
