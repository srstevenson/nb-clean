"""Tests for nb_clean.cli."""

from __future__ import annotations

import argparse
import io
import pathlib
import sys
from typing import TYPE_CHECKING, Collection, Iterable

import nb_clean.cli
import nbformat
import pytest

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from pytest_mock import MockerFixture


def test_expand_directories_with_files() -> None:
    """Test expanding directories when only files are present."""
    paths = [pathlib.Path("tests/notebooks/dirty.ipynb")]
    assert nb_clean.cli.expand_directories(paths) == paths


def test_expand_directories_recursively() -> None:
    """Test recursive expansion of directories."""
    input_paths = [pathlib.Path("tests")]
    expanded_paths = nb_clean.cli.expand_directories(input_paths)
    assert len(expanded_paths) > len(input_paths)
    assert all(path.is_file() and path.suffix == ".ipynb" for path in expanded_paths)


def test_exit_with_error(capsys: CaptureFixture[str], mocker: MockerFixture) -> None:
    """Test nb_clean.cli.exit_with_error."""
    mock_exit = mocker.patch("nb_clean.cli.sys.exit")
    nb_clean.cli.exit_with_error("error message", 42)
    assert capsys.readouterr().err == "nb-clean: error: error message\n"  # type: ignore[unreachable]
    mock_exit.assert_called_once_with(42)


def test_add_filter(mocker: MockerFixture) -> None:
    """Test nb_clean.cli.add_filter."""
    mock_add_git_filter = mocker.patch("nb_clean.add_git_filter")
    nb_clean.cli.add_filter(
        argparse.Namespace(
            remove_empty_cells=True,
            preserve_cell_metadata=None,
            preserve_cell_outputs=False,
            preserve_execution_counts=False,
        )
    )
    mock_add_git_filter.assert_called_once_with(
        remove_empty_cells=True,
        preserve_cell_metadata=None,
        preserve_cell_outputs=False,
        preserve_execution_counts=False,
    )


def test_add_filter_failure(mocker: MockerFixture) -> None:
    """Test nb_clean.cli.add_filter when call to Git fails."""
    mocker.patch(
        "nb_clean.add_git_filter",
        side_effect=nb_clean.GitProcessError(message="error message", return_code=42),
    )
    mock_exit_with_error = mocker.patch("nb_clean.cli.exit_with_error")
    nb_clean.cli.add_filter(
        argparse.Namespace(
            remove_empty_cells=True,
            preserve_cell_metadata=None,
            preserve_cell_outputs=False,
            preserve_execution_counts=False,
        )
    )
    mock_exit_with_error.assert_called_once_with("error message", 42)


def test_remove_filter(mocker: MockerFixture) -> None:
    """Test nb_clean.cli.remove_filter."""
    mock_remove_git_filter = mocker.patch("nb_clean.remove_git_filter")
    nb_clean.cli.remove_filter()
    mock_remove_git_filter.assert_called_once()


def test_remove_filter_failure(mocker: MockerFixture) -> None:
    """Test nb_clean.cli.remove_filter when call to Git fails."""
    mocker.patch(
        "nb_clean.remove_git_filter",
        side_effect=nb_clean.GitProcessError(message="error message", return_code=42),
    )
    mock_exit_with_error = mocker.patch("nb_clean.cli.exit_with_error")
    nb_clean.cli.remove_filter()
    mock_exit_with_error.assert_called_once_with("error message", 42)


@pytest.mark.parametrize(
    ("notebook", "clean"),
    [
        (pytest.lazy_fixture("clean_notebook"), True),  # type: ignore[operator]
        (pytest.lazy_fixture("dirty_notebook"), False),  # type: ignore[operator]
    ],
)
def test_check_file(
    mocker: MockerFixture, notebook: nbformat.NotebookNode, *, clean: bool
) -> None:
    """Test nb_clean.cli.check when input is file."""
    mock_read = mocker.patch("nb_clean.cli.nbformat.read", return_value=notebook)
    mock_check_notebook = mocker.patch("nb_clean.check_notebook", return_value=clean)
    mock_exit = mocker.patch("nb_clean.cli.sys.exit")
    nb_clean.cli.check(
        argparse.Namespace(
            inputs=[pathlib.Path("notebook.ipynb")],
            remove_empty_cells=False,
            preserve_cell_metadata=None,
            preserve_cell_outputs=False,
            preserve_execution_counts=False,
        )
    )
    mock_read.assert_called_once_with(
        pathlib.Path("notebook.ipynb"), as_version=nbformat.NO_CONVERT
    )
    mock_check_notebook.assert_called_once_with(
        notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=None,
        preserve_cell_outputs=False,
        preserve_execution_counts=False,
        filename="notebook.ipynb",
    )
    if clean:
        mock_exit.assert_not_called()
    else:
        mock_exit.assert_called_once_with(1)


@pytest.mark.parametrize(
    ("notebook", "clean"),
    [
        (pytest.lazy_fixture("clean_notebook"), True),  # type: ignore[operator]
        (pytest.lazy_fixture("dirty_notebook"), False),  # type: ignore[operator]
    ],
)
def test_check_stdin(
    mocker: MockerFixture, notebook: nbformat.NotebookNode, *, clean: bool
) -> None:
    """Test nb_clean.cli.check when input is stdin."""
    mocker.patch(
        "nb_clean.cli.sys.stdin", return_value=io.StringIO(nbformat.writes(notebook))  # type: ignore[no-untyped-call]
    )
    mock_read = mocker.patch("nb_clean.cli.nbformat.read", return_value=notebook)
    mock_check_notebook = mocker.patch("nb_clean.check_notebook", return_value=clean)
    mock_exit = mocker.patch("nb_clean.cli.sys.exit")
    nb_clean.cli.check(
        argparse.Namespace(
            inputs=[],
            remove_empty_cells=False,
            preserve_cell_metadata=None,
            preserve_cell_outputs=False,
            preserve_execution_counts=False,
        )
    )
    mock_read.assert_called_once_with(sys.stdin, as_version=nbformat.NO_CONVERT)
    mock_check_notebook.assert_called_once_with(
        notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=None,
        preserve_cell_outputs=False,
        preserve_execution_counts=False,
        filename="stdin",
    )
    if clean:
        mock_exit.assert_not_called()
    else:
        mock_exit.assert_called_once_with(1)


def test_clean_file(
    mocker: MockerFixture,
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.cli.clean when input is a file."""
    mock_read = mocker.patch("nb_clean.cli.nbformat.read", return_value=dirty_notebook)
    mock_clean_notebook = mocker.patch(
        "nb_clean.clean_notebook", return_value=clean_notebook
    )
    mock_write = mocker.patch("nb_clean.cli.nbformat.write")

    nb_clean.cli.clean(
        argparse.Namespace(
            inputs=[pathlib.Path("notebook.ipynb")],
            remove_empty_cells=False,
            preserve_cell_metadata=None,
            preserve_cell_outputs=False,
            preserve_execution_counts=False,
        )
    )

    mock_read.assert_called_once_with(
        pathlib.Path("notebook.ipynb"), as_version=nbformat.NO_CONVERT
    )
    mock_clean_notebook.assert_called_once_with(
        dirty_notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=None,
        preserve_cell_outputs=False,
        preserve_execution_counts=False,
    )
    mock_write.assert_called_once_with(clean_notebook, pathlib.Path("notebook.ipynb"))


def test_clean_stdin(
    capsys: CaptureFixture[str],
    mocker: MockerFixture,
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.cli.clean when input is stdin."""
    mocker.patch(
        "nb_clean.cli.sys.stdin",
        return_value=io.StringIO(nbformat.writes(dirty_notebook)),  # type: ignore[no-untyped-call]
    )
    mock_read = mocker.patch("nb_clean.cli.nbformat.read", return_value=dirty_notebook)
    mock_clean_notebook = mocker.patch(
        "nb_clean.clean_notebook", return_value=clean_notebook
    )

    nb_clean.cli.clean(
        argparse.Namespace(
            inputs=[],
            remove_empty_cells=False,
            preserve_cell_metadata=None,
            preserve_cell_outputs=False,
            preserve_execution_counts=False,
        )
    )

    mock_read.assert_called_once_with(sys.stdin, as_version=nbformat.NO_CONVERT)
    mock_clean_notebook.assert_called_once_with(
        dirty_notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=None,
        preserve_cell_outputs=False,
        preserve_execution_counts=False,
    )
    assert capsys.readouterr().out.strip() == nbformat.writes(clean_notebook)  # type: ignore[no-untyped-call]


@pytest.mark.parametrize(
    (
        "argv",
        "function",
        "inputs",
        "remove_empty_cells",
        "preserve_cell_metadata",
        "preserve_cell_outputs",
        "preserve_execution_counts",
    ),
    [
        ("add-filter -e", "add_filter", [], True, None, False, False),
        (
            "check -m -o a.ipynb b.ipynb",
            "check",
            "a.ipynb b.ipynb".split(),
            False,
            [],
            True,
            False,
        ),
        (
            "check -m tags -o a.ipynb b.ipynb",
            "check",
            "a.ipynb b.ipynb".split(),
            False,
            ["tags"],
            True,
            False,
        ),
        (
            "check -m tags special -o a.ipynb b.ipynb",
            "check",
            "a.ipynb b.ipynb".split(),
            False,
            ["tags", "special"],
            True,
            False,
        ),
        ("clean -e -o a.ipynb", "clean", ["a.ipynb"], True, None, True, False),
        ("clean -e -c -o a.ipynb", "clean", ["a.ipynb"], True, None, True, True),
    ],
)
def test_parse_args(
    argv: str,
    function: str,
    inputs: Iterable[str],
    *,
    remove_empty_cells: bool,
    preserve_cell_metadata: Collection[str] | None,
    preserve_cell_outputs: bool,
    preserve_execution_counts: bool,
) -> None:
    """Test nb_clean.cli.parse_args."""
    args = nb_clean.cli.parse_args(argv.split())
    assert args.func == getattr(nb_clean.cli, function)
    if inputs:
        assert args.inputs == [pathlib.Path(path) for path in inputs]
    assert args.remove_empty_cells is remove_empty_cells
    assert args.preserve_cell_metadata == preserve_cell_metadata
    assert args.preserve_cell_outputs is preserve_cell_outputs
    assert args.preserve_execution_counts is preserve_execution_counts
