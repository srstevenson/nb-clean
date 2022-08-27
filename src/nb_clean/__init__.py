"""Clean Jupyter notebooks of execution counts, metadata, and outputs."""

import contextlib
import pathlib
import subprocess

import nbformat

VERSION = "2.0.2"
GIT_ATTRIBUTES_LINE = "*.ipynb filter=nb-clean"


class GitProcessError(Exception):
    """Exception for errors executing Git.

    Parameters
    ----------
    message : str
        Error message.
    return_code : int
        Return code.

    """

    def __init__(self, message: str, return_code: int) -> None:
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
        process = subprocess.run(
            ["git"] + list(args), capture_output=True, check=True
        )
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
    remove_empty_cells: bool = False,
    preserve_cell_metadata: bool = False,
    preserve_cell_outputs: bool = False,
) -> None:
    """Add a filter to clean notebooks to the current Git repository.

    Parameters
    ----------
    remove_empty_cells : bool, default False
        If True, remove empty cells.
    preserve_cell_metadata : bool, default False
        If True, preserve cell metadata.
    preserve_cell_outputs : bool, default False
        If True, preserve cell outputs.

    """
    command = ["nb-clean", "clean"]

    if remove_empty_cells:
        command.append("--remove-empty-cells")

    if preserve_cell_metadata:
        command.append("--preserve-cell-metadata")

    if preserve_cell_outputs:
        command.append("--preserve-cell-outputs")

    git("config", "filter.nb-clean.clean", " ".join(command))

    attributes_path = git_attributes_path()

    if (
        attributes_path.is_file()
        and GIT_ATTRIBUTES_LINE in attributes_path.read_text(encoding="UTF-8")
    ):
        return

    with attributes_path.open("a", encoding="UTF-8") as file:
        file.write(f"\n{GIT_ATTRIBUTES_LINE}\n")


def remove_git_filter() -> None:
    """Remove the nb-clean filter from the current Git repository."""
    attributes_path = git_attributes_path()

    if attributes_path.is_file():
        original_contents = attributes_path.read_text(encoding="UTF-8").split(
            "\n"
        )
        revised_contents = [
            line for line in original_contents if line != GIT_ATTRIBUTES_LINE
        ]
        attributes_path.write_text(
            "\n".join(revised_contents), encoding="UTF-8"
        )

    git("config", "--remove-section", "filter.nb-clean")


def check_notebook(
    notebook: nbformat.NotebookNode,
    remove_empty_cells: bool = False,
    preserve_cell_metadata: bool = False,
    preserve_cell_outputs: bool = False,
    filename: str = "notebook",
) -> bool:
    """Check notebook is clean of execution counts, metadata, and outputs.

    Parameters
    ----------
    notebook : nbformat.NotebookNode
        The notebook.
    remove_empty_cells : bool, default False
        If True, also check for the presence of empty cells.
    preserve_cell_metadata : bool, default False
        If True, don't check for cell metadata.
    preserve_cell_outputs : bool, default False
        If True, don't check for cell outputs.
    filename : str, default "notebook"
        Notebook filename to use in log messages.

    Returns
    -------
    bool
        True if the notebook is clean, False otherwise.

    """
    is_clean = True

    for index, cell in enumerate(notebook.cells):
        prefix = f"{filename} cell {index}"

        if remove_empty_cells and not cell["source"]:
            print(f"{prefix}: empty cell")
            is_clean = False

        if not preserve_cell_metadata and cell["metadata"]:
            print(f"{prefix}: metadata")
            is_clean = False

        if cell["cell_type"] == "code":
            if cell["execution_count"]:
                print(f"{prefix}: execution count")
                is_clean = False
            if not preserve_cell_outputs and cell["outputs"]:
                print(f"{prefix}: outputs")
                is_clean = False

    with contextlib.suppress(KeyError):
        _ = notebook["metadata"]["language_info"]["version"]
        print(f"{filename} metadata: language_info.version")
        is_clean = False

    return is_clean


def clean_notebook(
    notebook: nbformat.NotebookNode,
    remove_empty_cells: bool = False,
    preserve_cell_metadata: bool = False,
    preserve_cell_outputs: bool = False,
) -> nbformat.NotebookNode:
    """Clean notebook of execution counts, metadata, and outputs.

    Parameters
    ----------
    notebook : nbformat.NotebookNode
        The notebook.
    remove_empty_cells : bool, default False
        If True, remove empty cells.
    preserve_cell_metadata : bool, default False
        If True, preserve cell metadata.
    preserve_cell_outputs : bool, default False
        If True, preserve cell outputs.

    Returns
    -------
    nbformat.NotebookNode
        The cleaned notebook.

    """
    if remove_empty_cells:
        notebook.cells = [cell for cell in notebook.cells if cell["source"]]

    for cell in notebook.cells:
        if not preserve_cell_metadata:
            cell["metadata"] = {}
        if cell["cell_type"] == "code":
            cell["execution_count"] = None
            if not preserve_cell_outputs:
                cell["outputs"] = []

    with contextlib.suppress(KeyError):
        del notebook["metadata"]["language_info"]["version"]

    return notebook
