<p align="center"><img src="images/nb-clean.png" width=300></p>

[![License](https://img.shields.io/github/license/srstevenson/nb-clean?label=License&color=blue)](https://github.com/srstevenson/nb-clean/blob/main/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/srstevenson/nb-clean?label=GitHub)](https://github.com/srstevenson/nb-clean)
[![PyPI version](https://img.shields.io/pypi/v/nb-clean?label=PyPI)](https://pypi.org/project/nb-clean/)
[![Python versions](https://img.shields.io/pypi/pyversions/nb-clean?label=Python)](https://pypi.org/project/nb-clean/)
[![CI status](https://github.com/srstevenson/nb-clean/workflows/CI/badge.svg)](https://github.com/srstevenson/nb-clean/actions)
[![Coverage](https://img.shields.io/codecov/c/gh/srstevenson/nb-clean?label=Coverage)](https://app.codecov.io/gh/srstevenson/nb-clean)

`nb-clean` cleans Jupyter notebooks of cell execution counts, metadata, outputs,
and (optionally) empty cells, preparing them for committing to version control.
It provides both a Git filter and pre-commit hook to automatically clean
notebooks before they're staged, and can also be used with other version control
systems, as a command line tool, and as a Python library. It can determine if a
notebook is clean or not, which can be used as a check in your continuous
integration pipelines.

> [!NOTE]
>
> `nb-clean` 2.0.0 introduced a new command line interface to make cleaning
> notebooks in place easier. If you upgrade from a previous release, you'll need
> to migrate to the new interface as described under
> [Migrating to `nb-clean` 2](#migrating-to-nb-clean-2).

## Installation

To install the latest release from [PyPI], use [pip]:

```bash
python3 -m pip install nb-clean
```

`nb-clean` can also be installed with [Conda]:

```bash
conda install -c conda-forge nb-clean
```

In Python projects using [Poetry] or [PDM] for dependency management, add
`nb-clean` as a development dependency with `poetry add --group dev nb-clean` or
`pdm add --dev nb-clean`. `nb-clean` requires Python 3.8 or later.

## Usage

### Checking

You can check if a notebook is clean with:

```bash
nb-clean check notebook.ipynb
```

or by passing the notebook contents on standard input:

```bash
nb-clean check < notebook.ipynb
```

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

`nb-clean` will exit with status code 0 if the notebook is clean, and status
code 1 if it is not. `nb-clean` will also print details of cell execution
counts, metadata, outputs, and empty cells it finds.

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

### Cleaning (Git filter)

To add a filter to an existing Git repository to automatically clean notebooks
when they're staged, run the following from the working tree:

```bash
nb-clean add-filter
```

This will configure a filter to remove cell execution counts, metadata, and
outputs. To also remove empty cells, use:

```bash
nb-clean add-filter --remove-empty-cells
```

To preserve cell metadata, such as that required by tools such as [papermill],
use:

```bash
nb-clean add-filter --preserve-cell-metadata
```

To preserve only specific cell metadata, e.g., `tags` and `special`, use:

```bash
nb-clean add-filter --preserve-cell-metadata tags special
```

To preserve cell outputs, use:

```bash
nb-clean add-filter --preserve-cell-outputs
```

To preserve cell execution counts, use:

```bash
nb-clean add-filter --preserve-execution-counts
```

To preserve notebook `language_info.version` metadata, use:

```bash
nb-clean add-filter --preserve-notebook-metadata
```

By default, `nb-clean` will not delete all notebook metadata. To completely
remove all notebook metadata:

```bash
nb-clean add-filter --remove-all-notebook-metadata
```

`nb-clean` will configure a filter in the Git repository in which it is run, and
won't mutate your global or system Git configuration. To remove the filter, run:

```bash
nb-clean remove-filter
```

### Cleaning (pre-commit hook)

`nb-clean` can also be used as a [pre-commit] hook. You may prefer this to the
Git filter if your project already uses the pre-commit framework.

Note that the Git filter and pre-commit hook work differently, with different
effects on your working directory. The pre-commit hook operates on the notebook
on disk, cleaning the copy in your working directory. The Git filter cleans
notebooks as they are added to the index, leaving the copy in your working
directory dirty. This means cell outputs are still visible to you in your local
Jupyter instance when using the Git filter, but not when using the pre-commit
hook.

After installing [pre-commit], add the `nb-clean` hook by adding the following
snippet to `.pre-commit-config.yaml` in the root of your repository:

```yaml
repos:
  - repo: https://github.com/srstevenson/nb-clean
    rev: 3.3.0
    hooks:
      - id: nb-clean
```

You can pass additional arguments to `nb-clean` with an `args` array. The
following example shows how to preserve only two specific metadata fields. Note
that, in the example, the final item `--` in the arg list is mandatory. The
option `--preserve-cell-metadata` may take an arbitrary number of field
arguments, and the `--` argument is needed to separate them from notebook
filenames, which `pre-commit` will append to the list of arguments.

```yaml
repos:
  - repo: https://github.com/srstevenson/nb-clean
    rev: 3.3.0
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
`pre-commit autoupdate` to update the hook to the latest release of `nb-clean`.

### Preserving all nbformat metadata

To ignore or preserve specifically the metadata defined in the
[`nbformat` documentation](https://nbformat.readthedocs.io/en/latest/format_description.html#cell-metadata),
use the following options:
`--preserve-cell-metadata collapsed scrolled deletable editable format name tags jupyter execution`.

### Migrating to `nb-clean` 2

The following table maps from the command line interface of `nb-clean` 1.6.0 to
that of `nb-clean` >=2.0.0.

The examples in the table use long flags, but short flags can also be used
instead.

| Description                                 | `nb-clean` 1.6.0                                                 | `nb-clean` >=2.0.0                                          |
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

Copyright © [Scott Stevenson].

`nb-clean` is distributed under the terms of the [ISC license].

[conda]: https://docs.conda.io/
[isc license]: https://opensource.org/licenses/ISC
[papermill]: https://papermill.readthedocs.io/
[pdm]: https://pdm.fming.dev/
[pip]: https://pip.pypa.io/
[poetry]: https://python-poetry.org/
[pre-commit]: https://pre-commit.com/
[pypi]: https://pypi.org/project/nb-clean/
[scott stevenson]: https://scott.stevenson.io
