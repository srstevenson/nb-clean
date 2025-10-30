<p align="center"><img src="images/nb-clean.png" width=300></p>

[![License](https://img.shields.io/github/license/srstevenson/nb-clean?label=License&color=blue)](https://github.com/srstevenson/nb-clean/blob/main/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/srstevenson/nb-clean?label=GitHub)](https://github.com/srstevenson/nb-clean)
[![PyPI version](https://img.shields.io/pypi/v/nb-clean?label=PyPI)](https://pypi.org/project/nb-clean/)
[![Python versions](https://img.shields.io/pypi/pyversions/nb-clean?label=Python)](https://pypi.org/project/nb-clean/)
[![CI status](https://github.com/srstevenson/nb-clean/workflows/CI/badge.svg)](https://github.com/srstevenson/nb-clean/actions)

nb-clean cleans Jupyter notebooks of cell execution counts, metadata, outputs,
and (optionally) empty cells, preparing them for committing to version control.
It provides both a Git filter and pre-commit hook to automatically clean
notebooks before they're staged, and can also be used with other version control
systems, as a command line tool, and as a Python library. It can determine if a
notebook is clean or not, which can be used as a check in your continuous
integration pipelines.

Jupyter notebooks contain execution metadata that changes every time you run a
cell, including execution counts, timestamps, and output data. When committed to
version control, these elements create unnecessary diff noise, make meaningful
code review difficult, and can accidentally expose sensitive information in cell
outputs. By cleaning notebooks before committing, you preserve only the
essential code and markdown content, leading to cleaner diffs, more focused
reviews, and better collaboration.

For a detailed discussion of the challenges notebooks present for version
control and collaborative development, see my [PyCon UK 2017 talk][pycon talk]
and accompanying [blog post][blog post].

> [!NOTE]
>
> nb-clean 2.0.0 introduced a new command line interface to make cleaning
> notebooks in place easier. If you upgrade from a previous release, you'll need
> to migrate to the new interface as described under
> [Migrating to nb-clean 2](#migrating-to-nb-clean-2).

## Installation

nb-clean requires Python 3.10 or later. To run the latest release of nb-clean in
an ephemeral virtual environment, use [uv]:

```bash
uvx nb-clean
```

To add nb-clean as a dependency to a Python project managed with uv, use:

```bash
uv add --dev nb-clean
```

## Command line usage

### Understanding notebook metadata

Jupyter notebooks contain several types of metadata that nb-clean can handle:

**Cell metadata** includes information attached to individual cells, such as
tags, slideshow settings, and execution timing. Cell metadata fields like
`collapsed`, `scrolled`, `deletable`, and `editable` control notebook interface
behaviour, whilst `tags` and custom fields support workflow automation.

**Notebook metadata** contains document-level information including the kernel
specification, language version, and notebook format version. The language
version information (`metadata.language_info.version`) frequently changes
between Python versions and creates unnecessary version control noise.

**Execution metadata** encompasses execution counts for code cells and their
outputs, along with execution timestamps and output data. This metadata changes
every time you run cells, regardless of whether the actual code has changed.

### Checking

You can check if a notebook is clean with:

```bash
nb-clean check notebook.ipynb
```

You can also process notebooks through standard input and output streams, which
is useful for integrating with shell pipelines or processing notebooks without
writing to disk:

```bash
nb-clean check < notebook.ipynb
```

When reading from standard input, nb-clean processes the notebook content
directly without accessing the filesystem. This approach is particularly useful
for automated workflows, continuous integration pipelines, or when you want to
check notebooks without creating temporary files.

The check can be run with the following flags:

- To check for empty cells use `--remove-empty-cells` or the short form `-e`.
- To ignore cell metadata use `--preserve-cell-metadata` or the short form `-m`.
  This will ignore all metadata fields. You can also pass a list of fields to
  ignore with `--preserve-cell-metadata field1 field2` or `-m field1 field2`.
  Note that when _not_ passing a list of fields, either the `-m` or
  `--preserve-cell-metadata` flag must be passed _after_ the notebook paths to
  process, or the notebook paths should be preceded with `--` so they are not
  interpreted as metadata fields.
- To ignore cell outputs use `--preserve-cell-outputs` or the short form `-o`.
- To ignore cell execution counts use `--preserve-execution-counts` or the short
  form `-c`.
- To ignore language version notebook metadata use
  `--preserve-notebook-metadata` or the short form `-n`.
- To check the notebook does not contain any notebook metadata use
  `--remove-all-notebook-metadata` or the short form `-M`.

For example, to check if a notebook is clean whilst ignoring notebook metadata:

```bash
nb-clean check --preserve-notebook-metadata notebook.ipynb
```

To check if a notebook is clean whilst ignoring all cell metadata:

```bash
nb-clean check --preserve-cell-metadata -- notebook.ipynb
```

To check if a notebook is clean whilst ignoring only the `tags` cell metadata
field:

```bash
nb-clean check --preserve-cell-metadata tags -- notebook.ipynb
```

nb-clean will exit with status code 0 if the notebook is clean, and status code
1 if it is not. nb-clean will also print details of cell execution counts,
metadata, outputs, and empty cells it finds.

Note that the conflicting options `--preserve-notebook-metadata` and
`--remove-all-notebook-metadata` cannot be used together, as they represent
contradictory instructions.

### Cleaning (interactive)

You can clean a Jupyter notebook with:

```bash
nb-clean clean notebook.ipynb
```

This cleans the notebook in place. You can also pass the notebook content on
standard input, in which case the cleaned notebook is written to standard
output:

```bash
nb-clean clean < original.ipynb > cleaned.ipynb
```

The cleaning can be run with the following flags:

- To remove empty cells use `--remove-empty-cells` or the short form `-e`.
- To preserve cell metadata use `--preserve-cell-metadata` or the short form
  `-m`. This will preserve all metadata fields. You can also pass a list of
  fields to preserve with `--preserve-cell-metadata field1 field2` or
  `-m field1 field2`. Note that when _not_ passing a list of fields, either the
  `-m` or `--preserve-cell-metadata` flag must be passed _after_ the notebook
  paths to process, or the notebook paths should be preceded with `--` so they
  are not interpreted as metadata fields.
- To preserve cell outputs use `--preserve-cell-outputs` or the short form `-o`.
- To preserve cell execution counts use `--preserve-execution-counts` or the
  short form `-c`.
- To preserve notebook metadata (such as language version) use
  `--preserve-notebook-metadata` or the short form `-n`.
- To remove all notebook metadata use `--remove-all-notebook-metadata` or the
  short form `-M`.

For example, to clean a notebook whilst preserving notebook metadata:

```bash
nb-clean clean --preserve-notebook-metadata notebook.ipynb
```

To clean a notebook whilst preserving all cell metadata:

```bash
nb-clean clean --preserve-cell-metadata -- notebook.ipynb
```

To clean a notebook whilst preserving only the `tags` cell metadata field:

```bash
nb-clean clean --preserve-cell-metadata tags -- notebook.ipynb
```

#### Directory processing

Both the `check` and `clean` commands can operate on directories as well as
individual notebook files. When you provide a directory path, nb-clean will
recursively find all `.ipynb` files within that directory and process them. For
example:

```bash
nb-clean check notebooks/
```

or

```bash
nb-clean clean experiments/
```

This is particularly useful for batch processing entire project directories or
ensuring all notebooks in a repository are clean.

### Cleaning (Git filter)

To add a filter to an existing Git repository to automatically clean notebooks
when they're staged, run the following from the working tree:

```bash
nb-clean add-filter
```

This will configure a filter to remove cell execution counts, metadata, and
outputs. The same flags as described above for
[interactive cleaning](#cleaning-interactive) can be passed to customise the
behaviour.

The Git filter operates by configuring the `filter.nb-clean.clean` setting in
your repository's local Git configuration and adding the line
`*.ipynb filter=nb-clean` to `.git/info/attributes`. This ensures that all
notebook files are automatically processed through nb-clean when staged for
commit. The filter configuration is local to the repository and won't affect
your global or system Git settings.

To remove the filter, run:

```bash
nb-clean remove-filter
```

### Cleaning (Jujutsu)

nb-clean can be used to clean notebooks tracked with [Jujutsu] rather than Git.
Configure Jujutsu to use nb-clean as a fix tool by adding the following snippet
to `~/.config/jj/config.toml`:

```toml
[fix.tools.nb-clean]
command = ["nb-clean", "clean"]
patterns = ["glob:'**/*.ipynb'"]
```

The same flags as described above for
[interactive cleaning](#cleaning-interactive) can be appended to the `command`
array to customise the behaviour.

Tracked notebooks can then be cleaned by running `jj fix`. See the [Jujutsu
documentation][jujutsu docs] for further details of how to invoke and configure
fix tools.

### Cleaning (pre-commit hook)

nb-clean can also be used as a [pre-commit] hook. You may prefer this to the Git
filter if your project already uses the pre-commit framework.

Note that the Git filter and pre-commit hook work differently, with different
effects on your working directory. The pre-commit hook operates on the notebook
on disk, cleaning the copy in your working directory. The Git filter cleans
notebooks as they are added to the index, leaving the copy in your working
directory dirty. This means cell outputs are still visible to you in your local
Jupyter instance when using the Git filter, but not when using the pre-commit
hook.

After installing [pre-commit], add the nb-clean hook by adding the following
snippet to `.pre-commit-config.yaml` in the root of your repository:

```yaml
repos:
  - repo: https://github.com/srstevenson/nb-clean
    rev: 4.0.1
    hooks:
      - id: nb-clean
```

You can pass additional arguments to nb-clean with an `args` array. The
following example shows how to preserve only two specific metadata fields. Note
that, in the example, the final item `--` in the arg list is mandatory. The
option `--preserve-cell-metadata` may take an arbitrary number of field
arguments, and the `--` argument is needed to separate them from notebook
filenames, which `pre-commit` will append to the list of arguments.

```yaml
repos:
  - repo: https://github.com/srstevenson/nb-clean
    rev: 4.0.1
    hooks:
      - id: nb-clean
        args:
          - --remove-empty-cells
          - --preserve-cell-metadata
          - tags
          - slideshow
          - --
```

Run `pre-commit install` to ensure the hook is installed, and
`pre-commit autoupdate` to update the hook to the latest release of nb-clean.

### Preserving all nbformat metadata

To ignore or preserve specifically the metadata defined in the
[`nbformat` documentation](https://nbformat.readthedocs.io/en/latest/format_description.html#cell-metadata),
use the following options:
`--preserve-cell-metadata collapsed scrolled deletable editable format name tags jupyter execution`.

## Python library usage

nb-clean can be used programmatically as a Python library, allowing integration
into other tools.

```python
import nbformat

import nb_clean

# Load a notebook
with open("notebook.ipynb") as f:
    notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)

# Check if the notebook is clean
is_clean = nb_clean.check_notebook(
    notebook, preserve_cell_outputs=True, filename="notebook.ipynb"
)

# Clean the notebook
cleaned_notebook = nb_clean.clean_notebook(
    notebook, remove_empty_cells=True, preserve_cell_metadata=["tags", "slideshow"]
)
```

The library functions accept the same configuration options as the command-line
interface. The `check_notebook()` function returns a boolean indicating whether
the notebook is clean, whilst `clean_notebook()` returns a cleaned copy of the
notebook.

## Migrating to nb-clean 2

The following table maps from the command line interface of nb-clean 1.6.0 to
that of nb-clean >=2.0.0.

The examples in the table use long flags, but short flags can also be used
instead.

| Description                                 | nb-clean 1.6.0                                                   | nb-clean >=2.0.0                                            |
| ------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------- |
| Clean notebook                              | `nb-clean clean --input notebook.ipynb \| sponge notebook.ipynb` | `nb-clean clean notebook.ipynb`                             |
| Clean notebook (remove empty cells)         | `nb-clean clean --input notebook.ipynb --remove-empty`           | `nb-clean clean --remove-empty-cells notebook.ipynb`        |
| Clean notebook (preserve all cell metadata) | `nb-clean clean --input notebook.ipynb --preserve-metadata`      | `nb-clean clean --preserve-cell-metadata -- notebook.ipynb` |
| Check notebook                              | `nb-clean check --input notebook.ipynb`                          | `nb-clean check notebook.ipynb`                             |
| Check notebook (ignore non-empty cells)     | `nb-clean check --input notebook.ipynb --remove-empty`           | `nb-clean check --remove-empty-cells notebook.ipynb`        |
| Check notebook (ignore all cell metadata)   | `nb-clean check --input notebook.ipynb --preserve-metadata`      | `nb-clean check --preserve-cell-metadata -- notebook.ipynb` |
| Add Git filter to clean notebooks           | `nb-clean configure-git`                                         | `nb-clean add-filter`                                       |
| Remove Git filter                           | `nb-clean unconfigure-git`                                       | `nb-clean remove-filter`                                    |

## Copyright

Copyright © Scott Stevenson.

nb-clean is distributed under the terms of the [ISC license].

[blog post]: https://srstevenson.com/posts/jupyter-notebooks-and-collaboration/
[isc license]: https://opensource.org/licenses/ISC
[jujutsu docs]: https://jj-vcs.github.io/jj/latest/cli-reference/#jj-fix
[jujutsu]: https://jj-vcs.github.io/jj/
[pre-commit]: https://pre-commit.com/
[pycon talk]: https://www.youtube.com/watch?v=J3k3HkVnd2c
[uv]: https://docs.astral.sh/uv/
