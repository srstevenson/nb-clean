"""Tests for nb-clean's Git integration."""

import pathlib
import subprocess
from typing import Collection, Union
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

import nb_clean


def test_git(mocker: MockerFixture) -> None:
    """Test nb_clean.git."""
    mock_process = Mock()
    mock_process.stdout = b" output string "
    mock_run = mocker.patch(
        "nb_clean.subprocess.run", return_value=mock_process
    )
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
        "preserve_cell_metadata",
        "preserve_cell_outputs",
        "filter_command",
    ),
    [
        (False, None, False, "nb-clean clean"),
        (True, None, False, "nb-clean clean --remove-empty-cells"),
        (False, [], False, "nb-clean clean --preserve-cell-metadata"),
        (
            False,
            ["tags"],
            False,
            "nb-clean clean --preserve-cell-metadata tags",
        ),
        (
            False,
            ["tags", "special"],
            False,
            "nb-clean clean --preserve-cell-metadata tags special",
        ),
        (False, None, True, "nb-clean clean --preserve-cell-outputs"),
        (
            True,
            [],
            True,
            "nb-clean clean --remove-empty-cells --preserve-cell-metadata --preserve-cell-outputs",
        ),
    ],
)
def test_add_git_filter(  # pylint: disable=too-many-arguments
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
    remove_empty_cells: bool,
    preserve_cell_metadata: Union[Collection[str], None],
    preserve_cell_outputs: bool,
    filter_command: str,
) -> None:
    """Test nb_clean.add_git_filter."""
    mock_git = mocker.patch("nb_clean.git")
    mock_git_attributes_path = mocker.patch(
        "nb_clean.git_attributes_path", return_value=tmp_path / "attributes"
    )
    nb_clean.add_git_filter(
        remove_empty_cells=remove_empty_cells,
        preserve_cell_metadata=preserve_cell_metadata,
        preserve_cell_outputs=preserve_cell_outputs,
    )
    mock_git.assert_called_once_with(
        "config", "filter.nb-clean.clean", filter_command
    )
    mock_git_attributes_path.assert_called_once()
    assert (
        nb_clean.GIT_ATTRIBUTES_LINE in (tmp_path / "attributes").read_text()
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
    assert (
        tmp_path / "attributes"
    ).read_text() == nb_clean.GIT_ATTRIBUTES_LINE


@pytest.mark.parametrize("filter_exists", [True, False])
def test_remove_git_filter(
    mocker: MockerFixture, tmp_path: pathlib.Path, filter_exists: bool
) -> None:
    """Test nb_clean.remove_git_filter."""
    mock_git = mocker.patch("nb_clean.git")
    mock_git_attributes_path = mocker.patch(
        "nb_clean.git_attributes_path",
        return_value=tmp_path / "attributes",
    )
    (tmp_path / "attributes").touch()
    if filter_exists:
        (tmp_path / "attributes").write_text(nb_clean.GIT_ATTRIBUTES_LINE)
    nb_clean.remove_git_filter()
    mock_git_attributes_path.assert_called_once()
    mock_git.assert_called_once_with(
        "config", "--remove-section", "filter.nb-clean"
    )
    if filter_exists:
        assert (
            nb_clean.GIT_ATTRIBUTES_LINE
            not in (tmp_path / "attributes").read_text()
        )
