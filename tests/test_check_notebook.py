"""Tests for nb_clean.check_notebook."""

from __future__ import annotations

from typing import TYPE_CHECKING, Collection

import nb_clean
import pytest

if TYPE_CHECKING:
    import nbformat


@pytest.mark.parametrize(
    ("notebook_name", "is_clean"),
    [
        ("clean_notebook", True),
        ("dirty_notebook", False),
        ("dirty_notebook_with_version", False),
    ],
)
def test_check_notebook(
    notebook_name: str, *, is_clean: bool, request: pytest.FixtureRequest
) -> None:
    """Test nb_clean.check_notebook."""
    notebook = request.getfixturevalue(notebook_name)
    assert nb_clean.check_notebook(notebook) is is_clean


@pytest.mark.parametrize("preserve_notebook_metadata", [True, False])
def test_check_notebook_preserve_notebook_metadata(
    clean_notebook_with_notebook_metadata: nbformat.NotebookNode,
    *,
    preserve_notebook_metadata: bool,
) -> None:
    """Test nb_clean.check_notebook when preserving notebook metadata."""
    assert (
        nb_clean.check_notebook(
            clean_notebook_with_notebook_metadata,
            preserve_notebook_metadata=preserve_notebook_metadata,
        )
        is preserve_notebook_metadata
    )


@pytest.mark.parametrize("remove_empty_cells", [True, False])
def test_check_notebook_remove_empty_cells(
    clean_notebook_with_empty_cells: nbformat.NotebookNode, *, remove_empty_cells: bool
) -> None:
    """Test nb_clean.check_notebook when removing empty cells."""
    output = nb_clean.check_notebook(
        clean_notebook_with_empty_cells, remove_empty_cells=remove_empty_cells
    )
    assert output is not remove_empty_cells


@pytest.mark.parametrize(
    "preserve_cell_metadata",
    [
        [],
        ["tags"],
        ["other"],
        ["tags", "special"],
        ["nbformat", "tags", "special"],
        None,
    ],
)
def test_check_notebook_preserve_cell_metadata(
    clean_notebook_with_cell_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Collection[str] | None,
) -> None:
    """Test nb_clean.check_notebook when preserving cell metadata."""
    expected = (preserve_cell_metadata is not None) and (
        preserve_cell_metadata == []
        or {"tags", "special", "nbclean"}.issubset(preserve_cell_metadata)
    )
    output = nb_clean.check_notebook(
        clean_notebook_with_cell_metadata, preserve_cell_metadata=preserve_cell_metadata
    )
    assert output is expected


@pytest.mark.parametrize(
    "preserve_cell_metadata",
    [
        [],
        ["tags"],
        ["other"],
        ["tags", "special"],
        ["nbformat", "tags", "special"],
        None,
    ],
)
def test_check_notebook_preserve_cell_metadata_tags(
    clean_notebook_with_tags_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Collection[str] | None,
) -> None:
    """Test nb_clean.check_notebook when preserving cell metadata."""
    expected = (preserve_cell_metadata is not None) and (
        preserve_cell_metadata == [] or {"tags"}.issubset(preserve_cell_metadata)
    )
    output = nb_clean.check_notebook(
        clean_notebook_with_tags_metadata, preserve_cell_metadata=preserve_cell_metadata
    )
    assert output is expected


@pytest.mark.parametrize(
    "preserve_cell_metadata",
    [
        [],
        ["tags"],
        ["other"],
        ["tags", "special"],
        ["nbformat", "tags", "special"],
        None,
    ],
)
def test_check_notebook_preserve_cell_metadata_tags_special(
    clean_notebook_with_tags_special_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Collection[str] | None,
) -> None:
    """Test nb_clean.check_notebook when preserving cell metadata."""
    expected = (preserve_cell_metadata is not None) and (
        preserve_cell_metadata == []
        or {"tags", "special"}.issubset(preserve_cell_metadata)
    )
    output = nb_clean.check_notebook(
        clean_notebook_with_tags_special_metadata,
        preserve_cell_metadata=preserve_cell_metadata,
    )
    assert output is expected


@pytest.mark.parametrize(
    ("notebook_name", "preserve_cell_outputs", "is_clean"),
    [
        ("clean_notebook_with_outputs", True, True),
        ("clean_notebook_with_outputs", False, False),
        ("clean_notebook_with_outputs_with_counts", True, False),
    ],
)
def test_check_notebook_preserve_outputs(
    notebook_name: str,
    *,
    preserve_cell_outputs: bool,
    is_clean: bool,
    request: pytest.FixtureRequest,
) -> None:
    """Test nb_clean.check_notebook when preserving cell outputs."""
    notebook = request.getfixturevalue(notebook_name)
    output = nb_clean.check_notebook(
        notebook, preserve_cell_outputs=preserve_cell_outputs
    )
    assert output is is_clean


@pytest.mark.parametrize(
    ("notebook_name", "preserve_execution_counts", "is_clean"),
    [
        ("clean_notebook_with_counts", True, True),
        ("clean_notebook_with_counts", False, False),
    ],
)
def test_check_notebook_preserve_execution_counts(
    notebook_name: str,
    *,
    preserve_execution_counts: bool,
    is_clean: bool,
    request: pytest.FixtureRequest,
) -> None:
    """Test nb_clean.check_notebook when preserving cell execution counts."""
    notebook = request.getfixturevalue(notebook_name)
    output = nb_clean.check_notebook(
        notebook, preserve_execution_counts=preserve_execution_counts
    )
    assert output is is_clean
