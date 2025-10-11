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
    from collections.abc import Collection, Iterable, Sequence


@dataclass
class Args(argparse.Namespace):
    """Arguments parsed from the command-line."""

    subcommand: str = ""
    inputs: list[Path] = field(default_factory=list)
    remove_empty_cells: bool = False
    remove_all_notebook_metadata: bool = False
    preserve_cell_metadata: list[str] | None = None
    preserve_cell_outputs: bool = False
    preserve_execution_counts: bool = False
    preserve_notebook_metadata: bool = False


def expand_directories(paths: Iterable[Path]) -> list[Path]:
    """Expand paths to directories into paths to notebooks contained within.

    Args:
        paths: Paths to expand, including directories.

    Returns:
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

    Args:
        message: Error message to print to standard error.
        return_code: Return code with which to exit.

    """
    print(f"nb-clean: error: {message}", file=sys.stderr)
    sys.exit(return_code)


def add_filter(
    *,
    remove_empty_cells: bool,
    remove_all_notebook_metadata: bool,
    preserve_cell_metadata: Collection[str] | None,
    preserve_cell_outputs: bool,
    preserve_execution_counts: bool,
    preserve_notebook_metadata: bool,
) -> None:
    """Add the nb-clean filter to the current Git repository.

    Args:
        remove_empty_cells: Configure the filter to remove empty cells.
        remove_all_notebook_metadata: Configure the filter to remove all notebook metadata.
        preserve_cell_metadata: Configure the filter to preserve cell metadata.
        preserve_cell_outputs: Configure the filter to preserve cell outputs.
        preserve_execution_counts: Configure the filter to preserve cell execution counts.
        preserve_notebook_metadata: Configure the filter to preserve notebook metadata such as language version.

    """
    try:
        nb_clean.add_git_filter(
            remove_empty_cells=remove_empty_cells,
            remove_all_notebook_metadata=remove_all_notebook_metadata,
            preserve_cell_metadata=preserve_cell_metadata,
            preserve_cell_outputs=preserve_cell_outputs,
            preserve_execution_counts=preserve_execution_counts,
            preserve_notebook_metadata=preserve_notebook_metadata,
        )
    except nb_clean.GitProcessError as exc:
        exit_with_error(exc.message, exc.return_code)


def remove_filter() -> None:
    """Remove the nb-clean filter from the current Git repository.

    This function removes the nb-clean filter configuration and cleans up
    the Git attributes file. If Git command execution fails, the program
    will exit with an appropriate error code.
    """
    try:
        nb_clean.remove_git_filter()
    except nb_clean.GitProcessError as exc:
        exit_with_error(exc.message, exc.return_code)


def check(
    inputs: Iterable[Path],
    *,
    remove_empty_cells: bool,
    remove_all_notebook_metadata: bool,
    preserve_cell_metadata: Collection[str] | None,
    preserve_cell_outputs: bool,
    preserve_execution_counts: bool,
    preserve_notebook_metadata: bool,
) -> None:
    """Check notebooks are clean of execution counts, metadata, and outputs.

    Args:
        inputs: Input notebook paths to check, empty list for stdin.
        remove_empty_cells: Check for the presence of empty cells.
        remove_all_notebook_metadata: Check for any notebook metadata.
        preserve_cell_metadata: Don't check for cell metadata.
        preserve_cell_outputs: Don't check for cell outputs.
        preserve_execution_counts: Don't check for cell execution counts.
        preserve_notebook_metadata: Don't check for notebook metadata such as language version.

    """
    if inputs:
        processed_inputs: list[Path] | list[TextIO] = expand_directories(inputs)
    else:
        processed_inputs = [sys.stdin]

    all_clean = True
    for input_ in processed_inputs:
        name = "stdin" if input_ is sys.stdin else os.fspath(cast("Path", input_))

        notebook = cast(
            "nbformat.NotebookNode",
            nbformat.read(input_, as_version=nbformat.NO_CONVERT),  # pyright: ignore[reportUnknownMemberType]
        )
        is_clean = nb_clean.check_notebook(
            notebook,
            remove_empty_cells=remove_empty_cells,
            remove_all_notebook_metadata=remove_all_notebook_metadata,
            preserve_cell_metadata=preserve_cell_metadata,
            preserve_cell_outputs=preserve_cell_outputs,
            preserve_execution_counts=preserve_execution_counts,
            preserve_notebook_metadata=preserve_notebook_metadata,
            filename=name,
        )
        all_clean &= is_clean

    if not all_clean:
        sys.exit(1)


def clean(
    inputs: Iterable[Path],
    *,
    remove_empty_cells: bool,
    remove_all_notebook_metadata: bool,
    preserve_cell_metadata: Collection[str] | None,
    preserve_cell_outputs: bool,
    preserve_execution_counts: bool,
    preserve_notebook_metadata: bool,
) -> None:
    """Clean notebooks of execution counts, metadata, and outputs.

    Args:
        inputs: Input notebook paths to clean, empty list for stdin.
        remove_empty_cells: Remove empty cells.
        remove_all_notebook_metadata: Remove all notebook metadata.
        preserve_cell_metadata: Don't clean cell metadata.
        preserve_cell_outputs: Don't clean cell outputs.
        preserve_execution_counts: Don't clean cell execution counts.
        preserve_notebook_metadata: Don't clean notebook metadata such as language version.

    """
    if inputs:
        processed_inputs: list[Path] | list[TextIO] = expand_directories(inputs)
        outputs = processed_inputs
    else:
        processed_inputs = [sys.stdin]
        outputs = [sys.stdout]

    for input_, output in zip(processed_inputs, outputs, strict=True):
        notebook = cast(
            "nbformat.NotebookNode",
            nbformat.read(input_, as_version=nbformat.NO_CONVERT),  # pyright: ignore[reportUnknownMemberType]
        )

        notebook = nb_clean.clean_notebook(
            notebook,
            remove_empty_cells=remove_empty_cells,
            remove_all_notebook_metadata=remove_all_notebook_metadata,
            preserve_cell_metadata=preserve_cell_metadata,
            preserve_cell_outputs=preserve_cell_outputs,
            preserve_execution_counts=preserve_execution_counts,
            preserve_notebook_metadata=preserve_notebook_metadata,
        )
        nbformat.write(notebook, output)  # pyright: ignore[reportUnknownMemberType]


def parse_args(args: Sequence[str]) -> Args:
    """Parse command line arguments and call corresponding function.

    Args:
        args: Command line arguments to parse.

    Returns:
        Parsed command line arguments.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    subparsers.add_parser("version", help="print version number")

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

    subparsers.add_parser(
        "remove-filter", help="remove Git filter that cleans notebooks before staging"
    )

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

    return parser.parse_args(args, namespace=Args())


def main() -> None:  # pragma: no cover
    """Command line entrypoint for nb-clean.

    Parses command line arguments and dispatches to the appropriate
    subcommand handler (version, add-filter, remove-filter, check, or clean).
    """
    args = parse_args(sys.argv[1:])

    if args.subcommand == "version":
        print(f"nb-clean {nb_clean.VERSION}")
    elif args.subcommand == "add-filter":
        add_filter(
            remove_empty_cells=args.remove_empty_cells,
            remove_all_notebook_metadata=args.remove_all_notebook_metadata,
            preserve_cell_metadata=args.preserve_cell_metadata,
            preserve_cell_outputs=args.preserve_cell_outputs,
            preserve_execution_counts=args.preserve_execution_counts,
            preserve_notebook_metadata=args.preserve_notebook_metadata,
        )
    elif args.subcommand == "remove-filter":
        remove_filter()
    elif args.subcommand == "check":
        check(
            args.inputs,
            remove_empty_cells=args.remove_empty_cells,
            remove_all_notebook_metadata=args.remove_all_notebook_metadata,
            preserve_cell_metadata=args.preserve_cell_metadata,
            preserve_cell_outputs=args.preserve_cell_outputs,
            preserve_execution_counts=args.preserve_execution_counts,
            preserve_notebook_metadata=args.preserve_notebook_metadata,
        )
    elif args.subcommand == "clean":
        clean(
            args.inputs,
            remove_empty_cells=args.remove_empty_cells,
            remove_all_notebook_metadata=args.remove_all_notebook_metadata,
            preserve_cell_metadata=args.preserve_cell_metadata,
            preserve_cell_outputs=args.preserve_cell_outputs,
            preserve_execution_counts=args.preserve_execution_counts,
            preserve_notebook_metadata=args.preserve_notebook_metadata,
        )
    else:
        # This should never happen due to argparse validation, but be defensive
        exit_with_error(f"Unknown subcommand: {args.subcommand}", 1)
