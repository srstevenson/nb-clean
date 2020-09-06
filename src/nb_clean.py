"""Clean Jupyter notebooks of execution counts, metadata, and outputs."""

import argparse
import pathlib
import subprocess
import sys
from typing import NoReturn

import nbformat

VERSION = "1.6.0"
ATTRIBUTE = "*.ipynb filter=nb-clean"


def error(message: str, code: int) -> NoReturn:
    """Print error message to stderr and exit with code.

    Parameters
    ----------
    message : str
        Error message, printed to stderr.
    code : int
        Exit code.

    """
    print(f"nb-clean: error: {message}", file=sys.stderr)
    sys.exit(code)


def git(*args: str) -> str:
    """Call a Git subcommand with arguments.

    Parameters
    ----------
    *args : str
        Git subcommand and arguments.

    Returns
    -------
    str
        stdout from Git.

    Examples
    --------
    >>> git('rev-parse', '--git-dir')
    .git

    """
    process = subprocess.run(
        ["git"] + list(args),
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        check=False,
    )

    if process.returncode:
        error(process.stderr.decode(), process.returncode)

    stdout: str = process.stdout.decode().strip()
    return stdout


def attributes_path() -> pathlib.Path:
    """Get path to the attributes file in the current Git repository.

    Returns
    -------
    pathlib.Path
        Path to the Git attributes file.

    Examples
    --------
    >>> attributes_path()
    PosixPath('.git/info/attributes')

    """
    git_dir = git("rev-parse", "--git-dir")
    return pathlib.Path(git_dir) / "info" / "attributes"


def print_version(args: argparse.Namespace) -> None:
    """Print the version number.

    Parameters
    ----------
    args : argparse.Namespace
        Unused.

    """
    del args  # Unused.
    print(f"nb-clean {VERSION}")


def configure_git(args: argparse.Namespace) -> None:
    """Add an nb-clean filter to the current Git repository.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments parsed from the command line. If args.remove_empty
        is True, configure the filter to remove empty cells. If
        args.preserve_metadata is True, configure the filter to preserve
        cell metadata.

    """
    command = ["nb-clean", "clean"]

    if args.remove_empty:
        command.append("--remove-empty")

    if args.preserve_metadata:
        command.append("--preserve-metadata")

    git("config", "filter.nb-clean.clean", " ".join(command))

    attributes = attributes_path()

    if attributes.is_file() and ATTRIBUTE in attributes.read_text():
        return

    with attributes.open("a") as file:
        file.write(f"\n{ATTRIBUTE}\n")


def unconfigure_git(args: argparse.Namespace) -> None:
    """Remove any nb-clean filter from the current Git repository.

    Parameters
    ----------
    args : argparse.Namespace
        Unused.

    """
    del args  # Unused.

    attributes = attributes_path()

    if attributes.is_file():
        original_contents = attributes.read_text().split("\n")
        revised_contents = [
            line for line in original_contents if line != ATTRIBUTE
        ]
        attributes.write_text("\n".join(revised_contents))

    git("config", "--remove-section", "filter.nb-clean")


def check(args: argparse.Namespace) -> None:
    """Check notebook is clean of execution counts, metadata, and outputs.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments parsed from the command line. If args.remove_empty
        is True, check for the presence of empty cells. If
        args.preserve_metadata is True, don't check for cell metadata.

    """
    notebook = nbformat.read(args.input, as_version=nbformat.NO_CONVERT)
    dirty = False

    for index, cell in enumerate(notebook.cells):
        prefix = f"{args.input.name} cell {index}"

        if args.remove_empty and len(cell["source"]) == 0:
            print(f"{prefix}: empty cell")
            dirty = True
        if not args.preserve_metadata and cell["metadata"]:
            print(f"{prefix}: metadata")
            dirty = True
        if cell["cell_type"] == "code":
            if cell["execution_count"]:
                print(f"{prefix}: execution count")
                dirty = True
            if cell["outputs"]:
                print(f"{prefix}: outputs")
                dirty = True

    if dirty:
        sys.exit(1)


def clean(args: argparse.Namespace) -> None:
    """Clean notebook of execution counts, metadata, and outputs.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments parsed from the command line. If args.remove_empty
        is True, remove empty cells. If args.preserve_metadata is True,
        preserve cell metadata.

    """
    notebook = nbformat.read(args.input, as_version=nbformat.NO_CONVERT)

    if args.remove_empty:
        notebook.cells = [
            cell for cell in notebook.cells if len(cell["source"]) > 0
        ]

    for cell in notebook.cells:
        if not args.preserve_metadata:
            cell["metadata"] = {}
        if cell["cell_type"] == "code":
            cell["execution_count"] = None
            cell["outputs"] = []

    nbformat.write(notebook, args.output)


def main() -> None:
    """Parse command line arguments and call corresponding function."""
    parser = argparse.ArgumentParser(allow_abbrev=False, description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    version_parser = subparsers.add_parser(
        "version", help="print version number"
    )
    version_parser.set_defaults(func=print_version)

    configure_parser = subparsers.add_parser(
        "configure-git",
        help="configure Git filter to clean notebooks before staging",
    )
    configure_parser.add_argument(
        "-e", "--remove-empty", action="store_true", help="remove empty cells"
    )
    configure_parser.add_argument(
        "-m",
        "--preserve-metadata",
        action="store_true",
        help="preserve cell metadata",
    )
    configure_parser.set_defaults(func=configure_git)

    unconfigure_parser = subparsers.add_parser(
        "unconfigure-git",
        help="remove Git filter that cleans notebooks before staging",
    )
    unconfigure_parser.set_defaults(func=unconfigure_git)

    check_parser = subparsers.add_parser(
        "check",
        help=(
            "check a notebook is clean of cell execution counts, metadata,"
            " and outputs"
        ),
    )
    check_parser.add_argument(
        "-i",
        "--input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="input file",
    )
    check_parser.add_argument(
        "-e",
        "--remove-empty",
        action="store_true",
        help="check for empty cells",
    )
    check_parser.add_argument(
        "-m",
        "--preserve-metadata",
        action="store_true",
        help="preserve cell metadata",
    )
    check_parser.set_defaults(func=check)

    clean_parser = subparsers.add_parser(
        "clean",
        help="clean notebook of cell execution counts, metadata, and outputs",
    )
    clean_parser.add_argument(
        "-i",
        "--input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="input file",
    )
    clean_parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="output file",
    )
    clean_parser.add_argument(
        "-e", "--remove-empty", action="store_true", help="remove empty cells"
    )
    clean_parser.add_argument(
        "-m",
        "--preserve-metadata",
        action="store_true",
        help="preserve cell metadata",
    )
    clean_parser.set_defaults(func=clean)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
