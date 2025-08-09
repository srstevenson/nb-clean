from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast

import nbformat
import pytest

import nb_clean
import nb_clean.cli

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable

    from pytest import CaptureFixture  # noqa: PT013


def test_expand_directories_with_files() -> None:
    paths = [Path("tests/notebooks/dirty.ipynb")]
    assert nb_clean.cli.expand_directories(paths) == paths


def test_expand_directories_recursively() -> None:
    input_paths = [Path("tests")]
    expanded_paths = nb_clean.cli.expand_directories(input_paths)
    assert len(expanded_paths) > len(input_paths)
    assert all(path.is_file() and path.suffix == ".ipynb" for path in expanded_paths)


def test_exit_with_error(capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        nb_clean.cli.exit_with_error("error message", 42)
    assert exc.value.code == 42
    assert capsys.readouterr().err == "nb-clean: error: error message\n"


def test_add_filter_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_add_git_filter(**kwargs: object) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(nb_clean, "add_git_filter", fake_add_git_filter)

    argv = ["nb-clean", "add-filter", "-e", "-n"]
    monkeypatch.setattr(sys, "argv", argv)
    nb_clean.cli.main()

    assert captured == {
        "remove_empty_cells": True,
        "remove_all_notebook_metadata": False,
        "preserve_cell_metadata": None,
        "preserve_cell_outputs": False,
        "preserve_execution_counts": False,
        "preserve_notebook_metadata": True,
    }


def test_add_filter_remove_all_notebook_metadata_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_add_git_filter(**kwargs: object) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(nb_clean, "add_git_filter", fake_add_git_filter)

    argv = ["nb-clean", "add-filter", "-e", "-M"]
    monkeypatch.setattr(sys, "argv", argv)
    nb_clean.cli.main()

    assert captured == {
        "remove_empty_cells": True,
        "remove_all_notebook_metadata": True,
        "preserve_cell_metadata": None,
        "preserve_cell_outputs": False,
        "preserve_execution_counts": False,
        "preserve_notebook_metadata": False,
    }


def test_add_filter_failure_dispatch(
    capsys: CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_add_git_filter(**_kwargs: object) -> None:
        raise nb_clean.GitProcessError(message="error message", return_code=42)

    monkeypatch.setattr(nb_clean, "add_git_filter", fake_add_git_filter)
    monkeypatch.setattr(sys, "argv", ["nb-clean", "add-filter", "-e", "-M"])

    with pytest.raises(SystemExit) as exc:
        nb_clean.cli.main()
    assert exc.value.code == 42
    assert capsys.readouterr().err == "nb-clean: error: error message\n"


def test_remove_filter_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"value": False}

    def fake_remove_git_filter() -> None:
        called["value"] = True

    monkeypatch.setattr(nb_clean, "remove_git_filter", fake_remove_git_filter)
    monkeypatch.setattr(sys, "argv", ["nb-clean", "remove-filter"])
    nb_clean.cli.main()
    assert called["value"]


def test_remove_filter_failure_dispatch(
    capsys: CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_remove_git_filter() -> None:
        raise nb_clean.GitProcessError(message="error message", return_code=42)

    monkeypatch.setattr(nb_clean, "remove_git_filter", fake_remove_git_filter)
    monkeypatch.setattr(sys, "argv", ["nb-clean", "remove-filter"])

    with pytest.raises(SystemExit) as exc:
        nb_clean.cli.main()
    assert exc.value.code == 42
    assert capsys.readouterr().err == "nb-clean: error: error message\n"


@pytest.mark.parametrize(
    ("name", "expect_exit"), [("clean.ipynb", False), ("dirty.ipynb", True)]
)
def test_check_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, *, expect_exit: bool
) -> None:
    src = Path("tests/notebooks") / name
    dst = tmp_path / name
    dst.write_bytes(src.read_bytes())

    monkeypatch.setattr(sys, "argv", ["nb-clean", "check", os.fspath(dst)])

    if expect_exit:
        with pytest.raises(SystemExit) as exc:
            nb_clean.cli.main()
        assert exc.value.code == 1
    else:
        nb_clean.cli.main()


@pytest.mark.parametrize(
    ("notebook_name", "expect_exit"),
    [("clean_notebook", False), ("dirty_notebook", True)],
)
def test_check_stdin(
    monkeypatch: pytest.MonkeyPatch,
    notebook_name: str,
    *,
    expect_exit: bool,
    request: pytest.FixtureRequest,
) -> None:
    notebook = cast(nbformat.NotebookNode, request.getfixturevalue(notebook_name))
    monkeypatch.setattr(sys, "argv", ["nb-clean", "check"])
    content = cast(str, nbformat.writes(notebook))  # pyright: ignore[reportUnknownMemberType]
    monkeypatch.setattr(sys, "stdin", io.StringIO(content))
    if expect_exit:
        with pytest.raises(SystemExit) as exc:
            nb_clean.cli.main()
        assert exc.value.code == 1
    else:
        nb_clean.cli.main()


def test_clean_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src_dirty = Path("tests/notebooks/dirty.ipynb")
    dst_dirty = tmp_path / "dirty.ipynb"
    dst_dirty.write_bytes(src_dirty.read_bytes())

    monkeypatch.setattr(sys, "argv", ["nb-clean", "clean", str(dst_dirty)])
    nb_clean.cli.main()

    cleaned = cast(
        nbformat.NotebookNode,
        nbformat.read(dst_dirty, as_version=nbformat.NO_CONVERT),  # pyright: ignore[reportUnknownMemberType]
    )
    expected = cast(
        nbformat.NotebookNode,
        nbformat.read(  # pyright: ignore[reportUnknownMemberType]
            Path("tests/notebooks/clean.ipynb"), as_version=nbformat.NO_CONVERT
        ),
    )
    assert cleaned == expected


def test_clean_stdin(
    capsys: CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    dirty = cast(
        nbformat.NotebookNode,
        nbformat.read(  # pyright: ignore[reportUnknownMemberType]
            Path("tests/notebooks/dirty.ipynb"), as_version=nbformat.NO_CONVERT
        ),
    )
    expected = cast(
        nbformat.NotebookNode,
        nbformat.read(  # pyright: ignore[reportUnknownMemberType]
            Path("tests/notebooks/clean.ipynb"), as_version=nbformat.NO_CONVERT
        ),
    )

    monkeypatch.setattr(sys, "argv", ["nb-clean", "clean"])
    dirty_content = cast(str, nbformat.writes(dirty))  # pyright: ignore[reportUnknownMemberType]
    monkeypatch.setattr(sys, "stdin", io.StringIO(dirty_content))

    nb_clean.cli.main()

    out = capsys.readouterr().out
    expected_text = cast(str, nbformat.writes(expected))  # pyright: ignore[reportUnknownMemberType]
    assert out.strip() == expected_text.strip()


@pytest.mark.parametrize(
    (
        "argv",
        "inputs",
        "remove_empty_cells",
        "remove_all_notebook_metadata",
        "preserve_cell_metadata",
        "preserve_cell_outputs",
        "preserve_execution_counts",
        "preserve_notebook_metadata",
    ),
    [
        ("add-filter -e", [], True, False, None, False, False, False),
        (
            "check -m -o a.ipynb b.ipynb",
            "a.ipynb b.ipynb".split(),
            False,
            False,
            [],
            True,
            False,
            False,
        ),
        (
            "check -m tags -o a.ipynb b.ipynb",
            "a.ipynb b.ipynb".split(),
            False,
            False,
            ["tags"],
            True,
            False,
            False,
        ),
        (
            "check -m tags special -o a.ipynb b.ipynb",
            "a.ipynb b.ipynb".split(),
            False,
            False,
            ["tags", "special"],
            True,
            False,
            False,
        ),
        ("clean -e -o a.ipynb", ["a.ipynb"], True, False, None, True, False, False),
        ("clean -e -c -o a.ipynb", ["a.ipynb"], True, False, None, True, True, False),
    ],
)
def test_parse_args(
    argv: str,
    inputs: Iterable[str],
    *,
    remove_empty_cells: bool,
    remove_all_notebook_metadata: bool,
    preserve_cell_metadata: Collection[str] | None,
    preserve_cell_outputs: bool,
    preserve_execution_counts: bool,
    preserve_notebook_metadata: bool,
) -> None:
    args = nb_clean.cli.parse_args(argv.split())
    if inputs:
        assert args.inputs == [Path(path) for path in inputs]
    assert args.remove_empty_cells is remove_empty_cells
    assert args.remove_all_notebook_metadata is remove_all_notebook_metadata
    assert args.preserve_cell_metadata == preserve_cell_metadata
    assert args.preserve_cell_outputs is preserve_cell_outputs
    assert args.preserve_execution_counts is preserve_execution_counts
    assert args.preserve_notebook_metadata is preserve_notebook_metadata
