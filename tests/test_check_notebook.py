"""Tests for nb_clean.check_notebook."""

import nbformat
import pytest

import nb_clean


@pytest.mark.parametrize(
    ("notebook", "is_clean"),
    [
        # pylint: disable=no-member
        (pytest.lazy_fixture("clean_notebook"), True),  # type: ignore[attr-defined]
        (pytest.lazy_fixture("dirty_notebook"), False),  # type: ignore[attr-defined]
        (pytest.lazy_fixture("dirty_notebook_with_version"), False),  # type: ignore[attr-defined]
    ],
)
def test_check_notebook(
    notebook: nbformat.NotebookNode, is_clean: bool
) -> None:
    """Test nb_clean.check_notebook."""
    assert nb_clean.check_notebook(notebook) is is_clean


@pytest.mark.parametrize("remove_empty_cells", [True, False])
def test_check_notebook_remove_empty_cells(
    clean_notebook_with_empty_cells: nbformat.NotebookNode,
    remove_empty_cells: bool,
) -> None:
    """Test nb_clean.check_notebook when removing empty cells."""
    assert (
        nb_clean.check_notebook(
            clean_notebook_with_empty_cells,
            remove_empty_cells=remove_empty_cells,
        )
        is not remove_empty_cells
    )


@pytest.mark.parametrize("preserve_cell_metadata", [True, False])
def test_check_notebook_preserve_metadata(
    clean_notebook_with_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: bool,
) -> None:
    """Test nb_clean.check_notebook when preserving cell metadata."""
    assert (
        nb_clean.check_notebook(
            clean_notebook_with_metadata,
            preserve_cell_metadata=preserve_cell_metadata,
        )
        is preserve_cell_metadata
    )
