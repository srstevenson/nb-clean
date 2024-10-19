"""Tests for nb-clean's Git integration."""

from __future__ import annotations

import pathlib
import subprocess
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

import nb_clean

if TYPE_CHECKING:
    from collections.abc import Collection

    from pytest_mock import MockerFixture


def test_git(mocker: MockerFixture) -> None:
    """Test nb_clean.git."""
    mock_process = Mock()
    mock_process.stdout = b" output string "
    mock_run = mocker.patch("nb_clean.subprocess.run", return_value=mock_process)
    output = nb_clean.git("command", "--flag")
    mock_run.assert_called_once_with(
        ["git", "command", "--flag"], capture_output=True, check=True
    )
    assert output == "output string"


def test_git_failure(mocker: MockerFixture) -> None:
    """Test nb_clean.git when call to Git fails."""
    mocker.patch(
        "nb_clean.subprocess.run",
        side_effect=subprocess.CalledProcessError(
            returncode=42, cmd="command", stderr=b"standard error"
        ),
    )
    with pytest.raises(nb_clean.GitProcessError) as exc:
        nb_clean.git("command", "--flag")
    assert exc.value.message == "standard error"
    assert exc.value.return_code == 42


def test_git_attributes_path(mocker: MockerFixture) -> None:
    """Test nb_clean.git_attributes_path."""
    mocker.patch("nb_clean.git", return_value="dir/.git")
    assert nb_clean.git_attributes_path() == pathlib.Path(
        "dir", ".git", "info", "attributes"
    )


@pytest.mark.parametrize(
    (
        "remove_empty_cells",
        "remove_all_notebook_metadata",
        "preserve_cell_metadata",
        "preserve_cell_outputs",
        "preserve_execution_counts",
        "preserve_notebook_metadata",
        "filter_command",
    ),
    [
        (False, False, None, False, False, False, "nb-clean clean"),
        (True, False, None, False, False, False, "nb-clean clean --remove-empty-cells"),
        (
            False,
            False,
            [],
            False,
            False,
            False,
            "nb-clean clean --preserve-cell-metadata",
        ),
        (
            False,
            False,
            ["tags"],
            False,
            False,
            False,
            "nb-clean clean --preserve-cell-metadata tags",
        ),
        (
            False,
            False,
            ["tags", "special"],
            False,
            False,
            False,
            "nb-clean clean --preserve-cell-metadata tags special",
        ),
        (
            False,
            False,
            None,
            True,
            False,
            False,
            "nb-clean clean --preserve-cell-outputs",
        ),
        (
            True,
            False,
            [],
            True,
            False,
            False,
            "nb-clean clean --remove-empty-cells --preserve-cell-metadata --preserve-cell-outputs",
        ),
        (
            False,
            False,
            None,
            False,
            True,
            True,
            "nb-clean clean --preserve-execution-counts --preserve-notebook-metadata",
        ),
        (
            False,
            True,
            None,
            False,
            False,
            False,
            "nb-clean clean --remove-all-notebook-metadata",
        ),
    ],
)
def test_add_git_filter(
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
    *,
    remove_empty_cells: bool,
    remove_all_notebook_metadata: bool,
    preserve_cell_metadata: Collection[str] | None,
    preserve_cell_outputs: bool,
    preserve_execution_counts: bool,
    preserve_notebook_metadata: bool,
    filter_command: str,
) -> None:
    """Test nb_clean.add_git_filter."""
    mock_git = mocker.patch("nb_clean.git")
    mock_git_attributes_path = mocker.patch(
        "nb_clean.git_attributes_path", return_value=tmp_path / "attributes"
    )
    nb_clean.add_git_filter(
        remove_empty_cells=remove_empty_cells,
        remove_all_notebook_metadata=remove_all_notebook_metadata,
        preserve_cell_metadata=preserve_cell_metadata,
        preserve_cell_outputs=preserve_cell_outputs,
        preserve_execution_counts=preserve_execution_counts,
        preserve_notebook_metadata=preserve_notebook_metadata,
    )
    mock_git.assert_called_once_with("config", "filter.nb-clean.clean", filter_command)
    mock_git_attributes_path.assert_called_once()
    assert nb_clean.GIT_ATTRIBUTES_LINE in (tmp_path / "attributes").read_text()


def test_add_git_filter_exclusive_arguments() -> None:
    """Test nb_clean.add_git_filter with invalid arguments."""
    with pytest.raises(
        ValueError,
        match="`preserve_notebook_metadata` and `remove_all_notebook_metadata` cannot both be `True`",
    ):
        nb_clean.add_git_filter(
            remove_all_notebook_metadata=True, preserve_notebook_metadata=True
        )


def test_add_git_filter_idempotent(
    mocker: MockerFixture, tmp_path: pathlib.Path
) -> None:
    """Test nb_clean.add_git_filter is idempotent."""
    mocker.patch("nb_clean.git")
    (tmp_path / "attributes").write_text(nb_clean.GIT_ATTRIBUTES_LINE)
    mock_git_attributes_path = mocker.patch(
        "nb_clean.git_attributes_path", return_value=tmp_path / "attributes"
    )
    nb_clean.add_git_filter()
    mock_git_attributes_path.assert_called_once()
    assert (tmp_path / "attributes").read_text() == nb_clean.GIT_ATTRIBUTES_LINE


@pytest.mark.parametrize("filter_exists", [True, False])
def test_remove_git_filter(
    mocker: MockerFixture, tmp_path: pathlib.Path, *, filter_exists: bool
) -> None:
    """Test nb_clean.remove_git_filter."""
    mock_git = mocker.patch("nb_clean.git")
    mock_git_attributes_path = mocker.patch(
        "nb_clean.git_attributes_path", return_value=tmp_path / "attributes"
    )
    (tmp_path / "attributes").touch()
    if filter_exists:
        (tmp_path / "attributes").write_text(nb_clean.GIT_ATTRIBUTES_LINE)
    nb_clean.remove_git_filter()
    mock_git_attributes_path.assert_called_once()
    mock_git.assert_called_once_with("config", "--remove-section", "filter.nb-clean")
    if filter_exists:
        assert nb_clean.GIT_ATTRIBUTES_LINE not in (tmp_path / "attributes").read_text()
