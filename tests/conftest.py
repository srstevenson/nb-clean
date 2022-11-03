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


@pytest.fixture()
def dirty_notebook() -> nbformat.NotebookNode:
    """A dirty notebook."""
    return read_notebook("dirty.ipynb")


@pytest.fixture()
def dirty_notebook_with_version() -> nbformat.NotebookNode:
    """A dirty notebook containing the Python version."""
    return read_notebook("dirty_with_version.ipynb")


@pytest.fixture()
def clean_notebook() -> nbformat.NotebookNode:
    """A clean notebook."""
    return read_notebook("clean.ipynb")


@pytest.fixture()
def clean_notebook_without_empty_cells() -> nbformat.NotebookNode:
    """A clean notebook without empty cells."""
    return read_notebook("clean_without_empty_cells.ipynb")


@pytest.fixture()
def clean_notebook_with_empty_cells() -> nbformat.NotebookNode:
    """A clean notebook containing empty cells."""
    return read_notebook("clean_with_empty_cells.ipynb")


@pytest.fixture()
def clean_notebook_with_cell_metadata() -> nbformat.NotebookNode:
    """A clean notebook with cell metadata."""
    return read_notebook("clean_with_cell_metadata.ipynb")


@pytest.fixture()
def clean_notebook_with_tags_metadata() -> nbformat.NotebookNode:
    """A clean notebook with only `tags` cell metadata."""
    return read_notebook("clean_with_tags_metadata.ipynb")


@pytest.fixture()
def clean_notebook_with_tags_special_metadata() -> nbformat.NotebookNode:
    """A clean notebook with only `tags` and `special` cell metadata."""
    return read_notebook("clean_with_tags_special_metadata.ipynb")


@pytest.fixture()
def clean_notebook_with_outputs() -> nbformat.NotebookNode:
    """A clean notebook with cell outputs."""
    return read_notebook("clean_with_outputs.ipynb")


@pytest.fixture()
def clean_notebook_with_outputs_with_counts() -> nbformat.NotebookNode:
    """A clean notebook with cell outputs and output execution counts."""
    return read_notebook("clean_with_outputs_with_counts.ipynb")


@pytest.fixture()
def clean_notebook_without_notebook_metadata() -> nbformat.NotebookNode:
    """A clean notebook without notebook metadata."""
    return read_notebook("clean_without_notebook_metadata.ipynb")
