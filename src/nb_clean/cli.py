"""Command line interface to nb-clean."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn, TextIO, cast

import nbformat

import nb_clean

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class Args(argparse.Namespace):
    """Arguments parsed from the command-line."""

    command: str = ""
    inputs: list[Path] = field(default_factory=list)
    remove_empty_cells: bool = False
    remove_all_notebook_metadata: bool = False
    preserve_cell_metadata: list[str] | None = None
    preserve_cell_outputs: bool = False
    preserve_execution_counts: bool = False
    preserve_notebook_metadata: bool = False
    func: Callable[[Args], None] = lambda _: None


def expand_directories(paths: list[Path]) -> list[Path]:
    """Expand paths to directories into paths to notebooks contained within.

    Parameters
    ----------
    paths : list[Path]
        Paths to expand, including directories.

    Returns
    -------
    list[Path]
        Paths with directories expanded into notebooks contained within.

    """
    expanded: set[Path] = set()
    for path in paths:
        if path.is_dir():
            expanded.update(path.rglob("*.ipynb"))
        else:
            expanded.add(path)
    return list(expanded)


def exit_with_error(message: str, return_code: int) -> NoReturn:
    """Print an error message to standard error and exit.

    Parameters
    ----------
    message : str
        Error message to print to standard error.
    return_code : int
        Return code with which to exit.

    """
    print(f"nb-clean: error: {message}", file=sys.stderr)
    sys.exit(return_code)


def add_filter(args: Args) -> None:
    """Add the nb-clean filter to the current Git repository.

    Parameters
    ----------
    args : Args
        Arguments parsed from the command line. If args.remove_empty_cells
        is True, configure the filter to remove empty cells. If
        args.preserve_cell_metadata is True, configure the filter to
        preserve cell metadata. If args.preserve_execution_counts is True,
        configure the filter to preserve cell execution counts. If
        args.preserve_notebook_metadata is True, configure the filter to
        preserve notebook metadata such as language version.

    """
    try:
        nb_clean.add_git_filter(
            remove_empty_cells=args.remove_empty_cells,
            remove_all_notebook_metadata=args.remove_all_notebook_metadata,
            preserve_cell_metadata=args.preserve_cell_metadata,
            preserve_cell_outputs=args.preserve_cell_outputs,
            preserve_execution_counts=args.preserve_execution_counts,
            preserve_notebook_metadata=args.preserve_notebook_metadata,
        )
    except nb_clean.GitProcessError as exc:
        exit_with_error(exc.message, exc.return_code)


def remove_filter() -> None:
    """Remove the nb-clean filter from the current repository."""
    try:
        nb_clean.remove_git_filter()
    except nb_clean.GitProcessError as exc:
        exit_with_error(exc.message, exc.return_code)


def check(args: Args) -> None:
    """Check notebooks are clean of execution counts, metadata, and outputs.

    Parameters
    ----------
    args : Args
        Arguments parsed from the command line. If args.remove_empty_cells
        is True, check for the presence of empty cells. If
        args.preserve_cell_metadata is True, don't check for cell metadata. If
        args.preserve_cell_outputs is True, don't check for cell outputs. If
        args.preserve_execution_counts is True, don't check for cell execution
        counts. If args.preserve_notebook_metadata is True, don't check for
        notebook metadata such as language version.

    """
    if args.inputs:
        inputs: list[Path] | list[TextIO] = expand_directories(args.inputs)
    else:
        inputs = [sys.stdin]

    all_clean = True
    for input_ in inputs:
        name = "stdin" if input_ is sys.stdin else os.fspath(cast(Path, input_))

        notebook = cast(
            nbformat.NotebookNode,
            nbformat.read(input_, as_version=nbformat.NO_CONVERT),  # pyright: ignore[reportUnknownMemberType]
        )
        is_clean = nb_clean.check_notebook(
            notebook,
            remove_empty_cells=args.remove_empty_cells,
            remove_all_notebook_metadata=args.remove_all_notebook_metadata,
            preserve_cell_metadata=args.preserve_cell_metadata,
            preserve_cell_outputs=args.preserve_cell_outputs,
            preserve_execution_counts=args.preserve_execution_counts,
            preserve_notebook_metadata=args.preserve_notebook_metadata,
            filename=name,
        )
        all_clean &= is_clean

    if not all_clean:
        sys.exit(1)


def clean(args: Args) -> None:
    """Clean notebooks of execution counts, metadata, and outputs.

    Parameters
    ----------
    args : Args
        Arguments parsed from the command line. If args.remove_empty_cells
        is True, check for empty cells. If args.preserve_cell_metadata is
        True, don't clean cell metadata. If args.preserve_cell_outputs is True,
        don't clean cell outputs. If args.preserve_execution_counts is True,
        don't clean cell execution counts. If args.preserve_notebook_metadata
        is True, don't clean notebook metadata such as language version.

    """
    if args.inputs:
        inputs: list[Path] | list[TextIO] = expand_directories(args.inputs)
        outputs = inputs
    else:
        inputs = [sys.stdin]
        outputs = [sys.stdout]

    for input_, output in zip(inputs, outputs):
        notebook = cast(
            nbformat.NotebookNode,
            nbformat.read(input_, as_version=nbformat.NO_CONVERT),  # pyright: ignore[reportUnknownMemberType]
        )

        notebook = nb_clean.clean_notebook(
            notebook,
            remove_empty_cells=args.remove_empty_cells,
            remove_all_notebook_metadata=args.remove_all_notebook_metadata,
            preserve_cell_metadata=args.preserve_cell_metadata,
            preserve_cell_outputs=args.preserve_cell_outputs,
            preserve_execution_counts=args.preserve_execution_counts,
            preserve_notebook_metadata=args.preserve_notebook_metadata,
        )
        nbformat.write(notebook, output)  # pyright: ignore[reportUnknownMemberType]


def parse_args(args: list[str]) -> Args:
    """Parse command line arguments and call corresponding function.

    Parameters
    ----------
    args : list[str]
        Command line arguments to parse.

    Returns
    -------
    Args
        Parsed command line arguments.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    version_parser = subparsers.add_parser("version", help="print version number")
    version_parser.set_defaults(func=lambda _: print(f"nb-clean {nb_clean.VERSION}"))  # pyright: ignore[reportUnknownLambdaType]

    add_filter_parser = subparsers.add_parser(
        "add-filter", help="add Git filter to clean notebooks before staging"
    )
    add_filter_parser.add_argument(
        "-e", "--remove-empty-cells", action="store_true", help="remove empty cells"
    )
    add_filter_parser.add_argument(
        "-M",
        "--remove-all-notebook-metadata",
        action="store_true",
        help="remove all notebook metadata",
    )
    add_filter_parser.add_argument(
        "-m",
        "--preserve-cell-metadata",
        default=None,
        nargs="*",
        help="preserve cell metadata, all unless fields are specified",
    )
    add_filter_parser.add_argument(
        "-o",
        "--preserve-cell-outputs",
        action="store_true",
        help="preserve cell outputs",
    )
    add_filter_parser.add_argument(
        "-c",
        "--preserve-execution-counts",
        action="store_true",
        help="preserve cell execution counts",
    )
    add_filter_parser.add_argument(
        "-n",
        "--preserve-notebook-metadata",
        action="store_true",
        help="preserve notebook metadata",
    )
    add_filter_parser.set_defaults(func=add_filter)

    remove_filter_parser = subparsers.add_parser(
        "remove-filter", help="remove Git filter that cleans notebooks before staging"
    )
    remove_filter_parser.set_defaults(func=lambda _: remove_filter())  # pyright: ignore[reportUnknownLambdaType]

    check_parser = subparsers.add_parser(
        "check",
        help=(
            "check a notebook is clean of cell execution counts, metadata, and outputs"
        ),
    )
    check_parser.add_argument(
        "inputs", nargs="*", metavar="PATH", type=Path, help="input file"
    )
    check_parser.add_argument(
        "-e", "--remove-empty-cells", action="store_true", help="check for empty cells"
    )
    check_parser.add_argument(
        "-M",
        "--remove-all-notebook-metadata",
        action="store_true",
        help="check for any notebook metadata",
    )
    check_parser.add_argument(
        "-m",
        "--preserve-cell-metadata",
        default=None,
        nargs="*",
        help="preserve cell metadata, all unless fields are specified",
    )
    check_parser.add_argument(
        "-o",
        "--preserve-cell-outputs",
        action="store_true",
        help="preserve cell outputs",
    )
    check_parser.add_argument(
        "-c",
        "--preserve-execution-counts",
        action="store_true",
        help="preserve cell execution counts",
    )
    check_parser.add_argument(
        "-n",
        "--preserve-notebook-metadata",
        action="store_true",
        help="preserve notebook metadata",
    )
    check_parser.set_defaults(func=check)

    clean_parser = subparsers.add_parser(
        "clean", help="clean notebook of cell execution counts, metadata, and outputs"
    )
    clean_parser.add_argument(
        "inputs", nargs="*", metavar="PATH", type=Path, help="input path"
    )
    clean_parser.add_argument(
        "-e", "--remove-empty-cells", action="store_true", help="remove empty cells"
    )
    clean_parser.add_argument(
        "-M",
        "--remove-all-notebook-metadata",
        action="store_true",
        help="remove all notebook metadata",
    )
    clean_parser.add_argument(
        "-m",
        "--preserve-cell-metadata",
        default=None,
        nargs="*",
        help="preserve cell metadata, all unless fields are specified",
    )
    clean_parser.add_argument(
        "-o",
        "--preserve-cell-outputs",
        action="store_true",
        help="preserve cell outputs",
    )
    clean_parser.add_argument(
        "-c",
        "--preserve-execution-counts",
        action="store_true",
        help="preserve cell execution counts",
    )
    clean_parser.add_argument(
        "-n",
        "--preserve-notebook-metadata",
        action="store_true",
        help="preserve notebook metadata",
    )
    clean_parser.set_defaults(func=clean)

    return parser.parse_args(args, namespace=Args())


def main() -> None:  # pragma: no cover
    """Command line entrypoint."""
    args = parse_args(sys.argv[1:])
    args.func(args)
