"""Command line interface to nb-clean."""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
from typing import NoReturn, TextIO, cast

import nbformat

import nb_clean


def expand_directories(paths: list[pathlib.Path]) -> list[pathlib.Path]:
    """Expand paths to directories into paths to notebooks contained within.

    Parameters
    ----------
    paths : list[pathlib.Path]
        Paths to expand, including directories.

    Returns
    -------
    list[pathlib.Path]
        Paths with directories expanded into notebooks contained within.

    """
    expanded: list[pathlib.Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(path.rglob("*.ipynb"))
        else:
            expanded.append(path)
    return list(set(expanded))


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


def add_filter(args: argparse.Namespace) -> None:
    """Add the nb-clean filter to the current Git repository.

    Parameters
    ----------
    args : argparse.Namespace
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


def check(args: argparse.Namespace) -> None:
    """Check notebooks are clean of execution counts, metadata, and outputs.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments parsed from the command line. If args.remove_empty_cells
        is True, check for the presence of empty cells. If
        args.preserve_cell_metadata is True, don't check for cell metadata. If
        args.preserve_cell_outputs is True, don't check for cell outputs. If
        args.preserve_execution_counts is True, don't check for cell execution
        counts. If args.preserve_notebook_metadata is True, don't check for
        notebook metadata such as language version.

    """
    if args.inputs:
        inputs: list[pathlib.Path] | list[TextIO] = expand_directories(args.inputs)
    else:
        inputs = [sys.stdin]

    states = []
    for input_ in inputs:
        name = "stdin" if input_ is sys.stdin else os.fspath(cast(pathlib.Path, input_))

        notebook = nbformat.read(input_, as_version=nbformat.NO_CONVERT)  # type: ignore[no-untyped-call]
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
        states.append(is_clean)

    if not all(states):
        sys.exit(1)


def clean(args: argparse.Namespace) -> None:
    """Clean notebooks of execution counts, metadata, and outputs.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments parsed from the command line. If args.remove_empty_cells
        is True, check for empty cells. If args.preserve_cell_metadata is
        True, don't clean cell metadata. If args.preserve_cell_outputs is True,
        don't clean cell outputs. If args.preserve_execution_counts is True,
        don't clean cell execution counts. If args.preserve_notebook_metadata
        is True, don't clean notebook metadata such as language version.

    """
    if args.inputs:
        inputs: list[pathlib.Path] | list[TextIO] = expand_directories(args.inputs)
        outputs = inputs
    else:
        inputs = [sys.stdin]
        outputs = [sys.stdout]

    for input_, output in zip(inputs, outputs):
        notebook = nbformat.read(input_, as_version=nbformat.NO_CONVERT)  # type: ignore[no-untyped-call]
        notebook = nb_clean.clean_notebook(
            notebook,
            remove_empty_cells=args.remove_empty_cells,
            remove_all_notebook_metadata=args.remove_all_notebook_metadata,
            preserve_cell_metadata=args.preserve_cell_metadata,
            preserve_cell_outputs=args.preserve_cell_outputs,
            preserve_execution_counts=args.preserve_execution_counts,
            preserve_notebook_metadata=args.preserve_notebook_metadata,
        )
        nbformat.write(notebook, output)  # type: ignore[no-untyped-call]


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments and call corresponding function.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    version_parser = subparsers.add_parser("version", help="print version number")
    version_parser.set_defaults(func=lambda _: print(f"nb-clean {nb_clean.VERSION}"))

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
    remove_filter_parser.set_defaults(func=lambda _: remove_filter())

    check_parser = subparsers.add_parser(
        "check",
        help=(
            "check a notebook is clean of cell execution counts, metadata, "
            "and outputs"
        ),
    )
    check_parser.add_argument(
        "inputs", nargs="*", metavar="PATH", type=pathlib.Path, help="input file"
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
        "inputs", nargs="*", metavar="PATH", type=pathlib.Path, help="input path"
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

    return parser.parse_args(args)


def main() -> None:  # pragma: no cover
    """Command line entrypoint."""
    args = parse_args(sys.argv[1:])
    args.func(args)
