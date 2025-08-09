from __future__ import annotations

from typing import TYPE_CHECKING, cast

import nbformat
import pytest

import nb_clean

if TYPE_CHECKING:
    from collections.abc import Collection


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
    notebook = cast(nbformat.NotebookNode, request.getfixturevalue(notebook_name))
    assert nb_clean.check_notebook(notebook) is is_clean


@pytest.mark.parametrize("preserve_notebook_metadata", [True, False])
def test_check_notebook_preserve_notebook_metadata(
    clean_notebook_with_notebook_metadata: nbformat.NotebookNode,
    *,
    preserve_notebook_metadata: bool,
) -> None:
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
    notebook = cast(nbformat.NotebookNode, request.getfixturevalue(notebook_name))
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
    notebook = cast(nbformat.NotebookNode, request.getfixturevalue(notebook_name))
    output = nb_clean.check_notebook(
        notebook, preserve_execution_counts=preserve_execution_counts
    )
    assert output is is_clean


@pytest.mark.parametrize(
    ("notebook_name", "remove_all_notebook_metadata", "is_clean"),
    [
        ("clean_notebook_with_notebook_metadata", True, False),
        ("clean_notebook_with_notebook_metadata", False, False),
        ("clean_notebook_without_notebook_metadata", True, True),
        ("clean_notebook_without_notebook_metadata", False, True),
        ("clean_notebook", True, False),
        ("clean_notebook", False, True),
    ],
)
def test_check_notebook_remove_all_notebook_metadata(
    notebook_name: str,
    *,
    remove_all_notebook_metadata: bool,
    is_clean: bool,
    request: pytest.FixtureRequest,
) -> None:
    # The test with `("clean_notebook_with_notebook_metadata", False, True)`
    # is False due to `clean_notebook_with_notebook_metadata` containing
    # `language_info.version` detected when `preserve_notebook_metadata=False`.
    notebook = cast(nbformat.NotebookNode, request.getfixturevalue(notebook_name))
    assert (
        nb_clean.check_notebook(
            notebook, remove_all_notebook_metadata=remove_all_notebook_metadata
        )
        == is_clean
    )


def test_check_notebook_exclusive_arguments(
    dirty_notebook: nbformat.NotebookNode,
) -> None:
    with pytest.raises(
        ValueError,
        match="`preserve_notebook_metadata` and `remove_all_notebook_metadata` cannot both be `True`",
    ):
        nb_clean.check_notebook(
            dirty_notebook,
            remove_all_notebook_metadata=True,
            preserve_notebook_metadata=True,
        )
