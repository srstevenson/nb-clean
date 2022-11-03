"""Tests for nb_clean.clean_notebook."""

from typing import Collection

import nbformat
import pytest

import nb_clean


def test_clean_notebook(
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.clean_notebook."""
    assert nb_clean.clean_notebook(dirty_notebook) == clean_notebook


def test_clean_notebook_with_version(
    dirty_notebook_with_version: nbformat.NotebookNode,
    clean_notebook: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.clean_notebook with language_info version."""
    assert (
        nb_clean.clean_notebook(dirty_notebook_with_version) == clean_notebook
    )


def test_clean_notebook_remove_empty_cells(
    clean_notebook_with_empty_cells: nbformat.NotebookNode,
    clean_notebook_without_empty_cells: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.clean_notebook when removing empty cells."""
    assert (
        nb_clean.clean_notebook(
            clean_notebook_with_empty_cells, remove_empty_cells=True
        )
        == clean_notebook_without_empty_cells
    )


@pytest.mark.parametrize(
    "preserve_cell_metadata",
    [
        [],
        ["nbclean", "tags", "special"],
        ["nbclean", "tags", "special", "toomany"],
    ],
)
def test_clean_notebook_preserve_metadata(
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook_with_cell_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Collection[str],
) -> None:
    """Test nb_clean.clean_notebook when preserving cell metadata."""
    assert (
        nb_clean.clean_notebook(
            dirty_notebook, preserve_cell_metadata=preserve_cell_metadata
        )
        == clean_notebook_with_cell_metadata
    )


@pytest.mark.parametrize(
    "preserve_cell_metadata", [["tags"], ["tags", "toomany"]]
)
def test_clean_notebook_preserve_metadata_tags(
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook_with_tags_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Collection[str],
) -> None:
    """Test nb_clean.clean_notebook when preserving only `tags` cell metadata."""
    assert (
        nb_clean.clean_notebook(
            dirty_notebook, preserve_cell_metadata=preserve_cell_metadata
        )
        == clean_notebook_with_tags_metadata
    )


@pytest.mark.parametrize(
    "preserve_cell_metadata",
    [["tags", "special"], ["tags", "special", "toomany"]],
)
def test_clean_notebook_preserve_metadata_tags_special(
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook_with_tags_special_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Collection[str],
) -> None:
    """Test nb_clean.clean_notebook when preserving only `tags` and `special` cell metadata."""
    assert (
        nb_clean.clean_notebook(
            dirty_notebook, preserve_cell_metadata=preserve_cell_metadata
        )
        == clean_notebook_with_tags_special_metadata
    )


def test_clean_notebook_preserve_outputs(
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook_with_outputs: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.clean_notebook when preserving cell outputs."""
    assert (
        nb_clean.clean_notebook(dirty_notebook, preserve_cell_outputs=True)
        == clean_notebook_with_outputs
    )


def test_clean_notebook_remove_notebook_metadata(
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook_without_notebook_metadata: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.clean_notebook when preserving cell outputs."""
    assert (
        nb_clean.clean_notebook(dirty_notebook, remove_notebook_metadata=True)
        == clean_notebook_without_notebook_metadata
    )
