"""Clean Jupyter notebooks of execution counts, metadata, and outputs."""

from __future__ import annotations

import contextlib
import pathlib
import subprocess
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Collection

    import nbformat
    from typing_extensions import Self

VERSION: Final = "4.0.1"
GIT_ATTRIBUTES_LINE: Final = "*.ipynb filter=nb-clean"


class GitProcessError(Exception):
    """Exception for errors executing Git."""

    def __init__(self: Self, message: str, return_code: int) -> None:
        """Exception for errors executing Git.

        Parameters
        ----------
        message : str
            Error message.
        return_code : int
            Return code.

        """
        super().__init__(message)
        self.message = message
        self.return_code = return_code


def git(*args: str) -> str:
    """Call a Git subcommand with arguments.

    Parameters
    ----------
    *args : str
        Git subcommand and arguments.

    Returns
    -------
    str
        Standard output from Git.

    Examples
    --------
    >>> git('rev-parse', '--git-dir')
    .git

    """
    try:
        process = subprocess.run(["git", *list(args)], capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise GitProcessError(exc.stderr.decode(), exc.returncode) from exc

    return process.stdout.decode().strip()


def git_attributes_path() -> pathlib.Path:
    """Get path to the attributes file in the current Git repository.

    Returns
    -------
    pathlib.Path
        Path to the attributes file.

    Examples
    --------
    >>> git_attributes_path()
    PosixPath('.git/info/attributes')

    """
    git_dir = git("rev-parse", "--git-dir")
    return pathlib.Path(git_dir, "info", "attributes")


def add_git_filter(
    *,
    remove_empty_cells: bool = False,
    remove_all_notebook_metadata: bool = False,
    preserve_cell_metadata: Collection[str] | None = None,
    preserve_cell_outputs: bool = False,
    preserve_execution_counts: bool = False,
    preserve_notebook_metadata: bool = False,
) -> None:
    """Add a filter to clean notebooks to the current Git repository.

    Parameters
    ----------
    remove_empty_cells : bool, default False
        If True, remove empty cells.
    remove_all_notebook_metadata : bool, default False
        If True, remove all notebook metadata.
    preserve_cell_metadata : list of str or None, default None
        If None, clean all cell metadata.
        If [], preserve all cell metadata.
        (This corresponds to the `-m` CLI option without specifying any fields.)
        If list of str, these are the cell metadata fields to preserve.
    preserve_cell_outputs : bool, default False
        If True, preserve cell outputs.
    preserve_execution_counts : bool, default False
        If True, preserve cell execution counts.
    preserve_notebook_metadata: bool, default False
        If True, preserve notebook metadata such as language version.

    """
    if preserve_notebook_metadata and remove_all_notebook_metadata:
        msg = "`preserve_notebook_metadata` and `remove_all_notebook_metadata` cannot both be `True`"
        raise ValueError(msg)

    command = ["nb-clean", "clean"]

    if remove_empty_cells:
        command.append("--remove-empty-cells")

    if preserve_cell_metadata is not None:
        if len(preserve_cell_metadata) > 0:
            command.append(
                f"--preserve-cell-metadata {' '.join(preserve_cell_metadata)}"
            )
        else:
            command.append("--preserve-cell-metadata")

    if preserve_cell_outputs:
        command.append("--preserve-cell-outputs")

    if preserve_execution_counts:
        command.append("--preserve-execution-counts")

    if preserve_notebook_metadata:
        command.append("--preserve-notebook-metadata")

    if remove_all_notebook_metadata:
        command.append("--remove-all-notebook-metadata")

    git("config", "filter.nb-clean.clean", " ".join(command))

    attributes_path = git_attributes_path()

    if attributes_path.is_file() and GIT_ATTRIBUTES_LINE in attributes_path.read_text(
        encoding="UTF-8"
    ):
        return

    with attributes_path.open("a", encoding="UTF-8") as file:
        file.write(f"\n{GIT_ATTRIBUTES_LINE}\n")


def remove_git_filter() -> None:
    """Remove the nb-clean filter from the current Git repository."""
    attributes_path = git_attributes_path()

    if attributes_path.is_file():
        original_contents = attributes_path.read_text(encoding="UTF-8").split("\n")
        revised_contents = [
            line for line in original_contents if line != GIT_ATTRIBUTES_LINE
        ]
        attributes_path.write_text("\n".join(revised_contents), encoding="UTF-8")

    git("config", "--remove-section", "filter.nb-clean")


def check_notebook(
    notebook: nbformat.NotebookNode,
    *,
    remove_empty_cells: bool = False,
    remove_all_notebook_metadata: bool = False,
    preserve_cell_metadata: Collection[str] | None = None,
    preserve_cell_outputs: bool = False,
    preserve_execution_counts: bool = False,
    preserve_notebook_metadata: bool = False,
    filename: str = "notebook",
) -> bool:
    """Check notebook is clean of execution counts, metadata, and outputs.

    Parameters
    ----------
    notebook : nbformat.NotebookNode
        The notebook.
    remove_empty_cells : bool, default False
        If True, also check for the presence of empty cells.
    remove_all_notebook_metadata : bool, default False
        If True, also check for the presence of any notebook metadata.
    preserve_cell_metadata : list of str or None, default None
        If None, check for all cell metadata.
        If [], don't check for any cell metadata.
        (This corresponds to the `-m` CLI option without specifying any fields.)
        If list of str, these are the cell metadata fields to ignore.
    preserve_cell_outputs : bool, default False
        If True, don't check for cell outputs.
    preserve_execution_counts : bool, default False
        If True, don't check for cell execution counts.
    preserve_notebook_metadata : bool, default False
        If True, preserve notebook metadata such as language version.
    filename : str, default "notebook"
        Notebook filename to use in log messages.

    Returns
    -------
    bool
        True if the notebook is clean, False otherwise.

    """
    if preserve_notebook_metadata and remove_all_notebook_metadata:
        msg = "`preserve_notebook_metadata` and `remove_all_notebook_metadata` cannot both be `True`"
        raise ValueError(msg)

    is_clean = True

    for index, cell in enumerate(notebook.cells):
        prefix = f"{filename} cell {index}"

        if remove_empty_cells and not cell["source"]:
            print(f"{prefix}: empty cell")
            is_clean = False

        if preserve_cell_metadata is None:
            if cell["metadata"]:
                print(f"{prefix}: metadata")
                is_clean = False
        elif len(preserve_cell_metadata) > 0:
            for field in cell["metadata"]:
                if field not in preserve_cell_metadata:
                    print(f"{prefix}: metadata {field}")
                    is_clean = False

        if cell["cell_type"] == "code":
            if not preserve_execution_counts and cell["execution_count"]:
                print(f"{prefix}: execution count")
                is_clean = False

            if preserve_cell_outputs:
                if not preserve_execution_counts:
                    for output in cell["outputs"]:
                        if output.get("execution_count") is not None:
                            print(f"{prefix}: output execution count")
                            is_clean = False
            elif cell["outputs"]:
                print(f"{prefix}: outputs")
                is_clean = False

    if remove_all_notebook_metadata and notebook.metadata:
        print(f"{filename}: metadata")
        is_clean = False

    if not preserve_notebook_metadata:
        with contextlib.suppress(KeyError):
            _ = notebook["metadata"]["language_info"]["version"]
            print(f"{filename} metadata: language_info.version")
            is_clean = False

    return is_clean


def clean_notebook(
    notebook: nbformat.NotebookNode,
    *,
    remove_empty_cells: bool = False,
    remove_all_notebook_metadata: bool = False,
    preserve_cell_metadata: Collection[str] | None = None,
    preserve_cell_outputs: bool = False,
    preserve_execution_counts: bool = False,
    preserve_notebook_metadata: bool = False,
) -> nbformat.NotebookNode:
    """Clean notebook of execution counts, metadata, and outputs.

    Parameters
    ----------
    notebook : nbformat.NotebookNode
        The notebook.
    remove_empty_cells : bool, default False
        If True, remove empty cells.
    remove_all_notebook_metadata : bool, default False
        If True, remove all notebook metadata.
    preserve_cell_metadata : list of str or None, default None
        If None, clean all cell metadata.
        If [], preserve all cell metadata.
        (This corresponds to the `-m` CLI option without specifying any fields.)
        If list of str, these are the cell metadata fields to preserve.
    preserve_cell_outputs : bool, default False
        If True, preserve cell outputs.
    preserve_execution_counts : bool, default False
        If True, preserve cell execution counts.
    preserve_notebook_metadata : bool, default False
        If True, preserve notebook metadata such as language version.

    Returns
    -------
    nbformat.NotebookNode
        The cleaned notebook.

    """
    if preserve_notebook_metadata and remove_all_notebook_metadata:
        msg = "`preserve_notebook_metadata` and `remove_all_notebook_metadata` cannot both be `True`"
        raise ValueError(msg)

    if remove_empty_cells:
        notebook.cells = [cell for cell in notebook.cells if cell["source"]]

    for cell in notebook.cells:
        if preserve_cell_metadata is None:
            cell["metadata"] = {}
        elif len(preserve_cell_metadata) > 0:
            cell["metadata"] = {
                field: value
                for field, value in cell["metadata"].items()
                if field in preserve_cell_metadata
            }
        if cell["cell_type"] == "code":
            if not preserve_execution_counts:
                cell["execution_count"] = None
            if preserve_cell_outputs:
                if not preserve_execution_counts:
                    for output in cell["outputs"]:
                        if "execution_count" in output:
                            output["execution_count"] = None
            else:
                cell["outputs"] = []

    if remove_all_notebook_metadata:
        notebook.metadata = {}
    elif not preserve_notebook_metadata:
        with contextlib.suppress(KeyError):
            del notebook["metadata"]["language_info"]["version"]

    return notebook
