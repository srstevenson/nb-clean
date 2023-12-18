"""Tests for nb_clean.clean_notebook."""

from typing import Collection

import nb_clean
import nbformat
import pytest


def test_clean_notebook(
    dirty_notebook: nbformat.NotebookNode, clean_notebook: nbformat.NotebookNode
) -> None:
    """Test nb_clean.clean_notebook."""
    assert nb_clean.clean_notebook(dirty_notebook) == clean_notebook


@pytest.mark.parametrize(
    ("preserve_notebook_metadata", "expected_output"),
    [
        (True, pytest.lazy_fixture("clean_notebook_with_notebook_metadata")),  # type: ignore[operator]
        (False, pytest.lazy_fixture("clean_notebook")),  # type: ignore[operator]
    ],
)
def test_clean_notebook_with_notebook_metadata(
    clean_notebook_with_notebook_metadata: nbformat.NotebookNode,
    *,
    preserve_notebook_metadata: bool,
    expected_output: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.clean_notebook with notebook metadata."""
    assert (
        nb_clean.clean_notebook(
            clean_notebook_with_notebook_metadata,
            preserve_notebook_metadata=preserve_notebook_metadata,
        )
        == expected_output
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
    [[], ["nbclean", "tags", "special"], ["nbclean", "tags", "special", "toomany"]],
)
def test_clean_notebook_preserve_cell_metadata(
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


@pytest.mark.parametrize("preserve_cell_metadata", [["tags"], ["tags", "toomany"]])
def test_clean_notebook_preserve_cell_metadata_tags(
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
    "preserve_cell_metadata", [["tags", "special"], ["tags", "special", "toomany"]]
)
def test_clean_notebook_preserve_cell_metadata_tags_special(
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


def test_clean_notebook_preserve_execution_counts(
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook_with_counts: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.clean_notebook when preserving cell execution counts."""
    assert (
        nb_clean.clean_notebook(dirty_notebook, preserve_execution_counts=True)
        == clean_notebook_with_counts
    )
