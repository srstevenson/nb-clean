"""Tests for nb_clean.cli."""

import argparse
import io
import pathlib
import sys

import nbformat
import pytest
from pytest_mock import MockerFixture

import nb_clean


def test_exit_with_error(capsys, mocker: MockerFixture) -> None:
    """Test nb_clean.cli.exit_with_error."""
    mock_exit = mocker.patch("nb_clean.cli.sys.exit")
    nb_clean.cli.exit_with_error("error message", 42)
    assert capsys.readouterr().err == "nb-clean: error: error message\n"
    mock_exit.assert_called_once_with(42)


def test_add_filter(mocker: MockerFixture) -> None:
    """Test nb_clean.cli.add_filter."""
    mock_add_git_filter = mocker.patch("nb_clean.add_git_filter")
    nb_clean.cli.add_filter(
        argparse.Namespace(
            remove_empty_cells=True, preserve_cell_metadata=False
        )
    )
    mock_add_git_filter.assert_called_once_with(
        remove_empty_cells=True, preserve_cell_metadata=False
    )


def test_add_filter_failure(mocker: MockerFixture) -> None:
    """Test nb_clean.cli.add_filter when call to Git fails."""
    mocker.patch(
        "nb_clean.add_git_filter",
        side_effect=nb_clean.GitProcessError(
            message="error message", return_code=42
        ),
    )
    mock_exit_with_error = mocker.patch("nb_clean.cli.exit_with_error")
    nb_clean.cli.add_filter(
        argparse.Namespace(
            remove_empty_cells=True, preserve_cell_metadata=False
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
        side_effect=nb_clean.GitProcessError(
            message="error message", return_code=42
        ),
    )
    mock_exit_with_error = mocker.patch("nb_clean.cli.exit_with_error")
    nb_clean.cli.remove_filter()
    mock_exit_with_error.assert_called_once_with("error message", 42)


@pytest.mark.parametrize(
    "notebook,clean",
    [
        # pylint: disable=no-member
        (pytest.lazy_fixture("clean_notebook"), True),  # type: ignore
        (pytest.lazy_fixture("dirty_notebook"), False),  # type: ignore
    ],
)
def test_check_file(
    mocker: MockerFixture, notebook: nbformat.NotebookNode, clean: bool
) -> None:
    """Test nb_clean.cli.check when input is file."""
    mock_read = mocker.patch(
        "nb_clean.cli.nbformat.read", return_value=notebook
    )
    mock_check_notebook = mocker.patch(
        "nb_clean.check_notebook", return_value=clean
    )
    mock_exit = mocker.patch("nb_clean.cli.sys.exit")
    nb_clean.cli.check(
        argparse.Namespace(
            inputs=[pathlib.Path("notebook.ipynb")],
            remove_empty_cells=False,
            preserve_cell_metadata=False,
        )
    )
    mock_read.assert_called_once_with(
        pathlib.Path("notebook.ipynb"), as_version=nbformat.NO_CONVERT
    )
    mock_check_notebook.assert_called_once_with(
        notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=False,
        filename="notebook.ipynb",
    )
    if clean:
        mock_exit.assert_not_called()
    else:
        mock_exit.assert_called_once_with(1)


@pytest.mark.parametrize(
    "notebook,clean",
    [
        # pylint: disable=no-member
        (pytest.lazy_fixture("clean_notebook"), True),  # type: ignore
        (pytest.lazy_fixture("dirty_notebook"), False),  # type: ignore
    ],
)
def test_check_stdin(
    mocker: MockerFixture,
    notebook: nbformat.NotebookNode,
    clean: bool,
) -> None:
    """Test nb_clean.cli.check when input is stdin."""
    mocker.patch(
        "nb_clean.cli.sys.stdin",
        return_value=io.StringIO(nbformat.writes(notebook)),
    )
    mock_read = mocker.patch(
        "nb_clean.cli.nbformat.read", return_value=notebook
    )
    mock_check_notebook = mocker.patch(
        "nb_clean.check_notebook", return_value=clean
    )
    mock_exit = mocker.patch("nb_clean.cli.sys.exit")
    nb_clean.cli.check(
        argparse.Namespace(
            inputs=[],
            remove_empty_cells=False,
            preserve_cell_metadata=False,
        )
    )
    mock_read.assert_called_once_with(
        sys.stdin, as_version=nbformat.NO_CONVERT
    )
    mock_check_notebook.assert_called_once_with(
        notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=False,
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
    mock_read = mocker.patch(
        "nb_clean.cli.nbformat.read", return_value=dirty_notebook
    )
    mock_clean_notebook = mocker.patch(
        "nb_clean.clean_notebook", return_value=clean_notebook
    )
    mock_write = mocker.patch("nb_clean.cli.nbformat.write")

    nb_clean.cli.clean(
        argparse.Namespace(
            inputs=[pathlib.Path("notebook.ipynb")],
            remove_empty_cells=False,
            preserve_cell_metadata=False,
        )
    )

    mock_read.assert_called_once_with(
        pathlib.Path("notebook.ipynb"), as_version=nbformat.NO_CONVERT
    )
    mock_clean_notebook.assert_called_once_with(
        dirty_notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=False,
    )
    mock_write.assert_called_once_with(
        clean_notebook, pathlib.Path("notebook.ipynb")
    )


def test_clean_stdin(
    capsys,
    mocker: MockerFixture,
    dirty_notebook: nbformat.NotebookNode,
    clean_notebook: nbformat.NotebookNode,
) -> None:
    """Test nb_clean.cli.clean when input is stdin."""
    mocker.patch(
        "nb_clean.cli.sys.stdin",
        return_value=io.StringIO(nbformat.writes(dirty_notebook)),
    )
    mock_read = mocker.patch(
        "nb_clean.cli.nbformat.read", return_value=dirty_notebook
    )
    mock_clean_notebook = mocker.patch(
        "nb_clean.clean_notebook", return_value=clean_notebook
    )

    nb_clean.cli.clean(
        argparse.Namespace(
            inputs=[],
            remove_empty_cells=False,
            preserve_cell_metadata=False,
        )
    )

    mock_read.assert_called_once_with(
        sys.stdin, as_version=nbformat.NO_CONVERT
    )
    mock_clean_notebook.assert_called_once_with(
        dirty_notebook,
        remove_empty_cells=False,
        preserve_cell_metadata=False,
    )
    assert capsys.readouterr().out.strip() == nbformat.writes(clean_notebook)
