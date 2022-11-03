"""Tests for nb_clean.check_notebook."""

from typing import Collection, Union

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
    output = nb_clean.check_notebook(
        clean_notebook_with_empty_cells,
        remove_empty_cells=remove_empty_cells,
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
def test_check_notebook_preserve_metadata(
    clean_notebook_with_cell_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Union[Collection[str], None],
) -> None:
    """Test nb_clean.check_notebook when preserving cell metadata."""
    expected = (preserve_cell_metadata is not None) and (
        preserve_cell_metadata == []
        or {"tags", "special", "nbclean"}.issubset(preserve_cell_metadata)
    )
    output = nb_clean.check_notebook(
        clean_notebook_with_cell_metadata,
        preserve_cell_metadata=preserve_cell_metadata,
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
def test_check_notebook_preserve_metadata_tags(
    clean_notebook_with_tags_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Union[Collection[str], None],
) -> None:
    """Test nb_clean.check_notebook when preserving cell metadata."""
    expected = (preserve_cell_metadata is not None) and (
        preserve_cell_metadata == []
        or {"tags"}.issubset(preserve_cell_metadata)
    )
    output = nb_clean.check_notebook(
        clean_notebook_with_tags_metadata,
        preserve_cell_metadata=preserve_cell_metadata,
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
def test_check_notebook_preserve_metadata_tags_special(
    clean_notebook_with_tags_special_metadata: nbformat.NotebookNode,
    preserve_cell_metadata: Union[Collection[str], None],
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
    ("notebook", "preserve_cell_outputs", "is_clean"),
    [
        # pylint: disable=no-member
        (
            pytest.lazy_fixture("clean_notebook_with_outputs"),  # type: ignore[attr-defined]
            True,
            True,
        ),
        (
            pytest.lazy_fixture("clean_notebook_with_outputs"),  # type: ignore[attr-defined]
            False,
            False,
        ),
        (
            pytest.lazy_fixture("clean_notebook_with_outputs_with_counts"),  # type: ignore[attr-defined]
            True,
            False,
        ),
    ],
)
def test_check_notebook_preserve_outputs(
    notebook: nbformat.NotebookNode,
    preserve_cell_outputs: bool,
    is_clean: bool,
) -> None:
    """Test nb_clean.check_notebook when preserving cell outputs."""
    output = nb_clean.check_notebook(
        notebook,
        preserve_cell_outputs=preserve_cell_outputs,
    )
    assert output is is_clean
