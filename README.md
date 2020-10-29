# nb-clean

`nb-clean` cleans Jupyter notebooks of cell execution counts, metadata, outputs,
and (optionally) empty cells, preparing them for committing to version control.
It provides a Git filter to automatically clean notebooks before they're staged,
and can also be used with other version control systems, as a command line tool,
and as a Python library. It can determine if a notebook is clean or not, which
can be used as a check in your continuous integration pipelines.

:warning: _`nb-clean` 2.0.0 introduced a new command line interface to make
cleaning notebooks in place easier. If you upgrade from a previous release,
you'll need to migrate to the new interface as described under
[Migrating to `nb-clean` 2](#migrating-to-nb-clean-2)._

## Installation

To install the latest release from [PyPI], use [pip]:

```bash
python3 -m pip install nb-clean
```

Alternately, in Python projects using [Poetry] or [Pipenv] for dependency
management, add `nb-clean` as a development dependency with
`poetry add --dev nb-clean` or `pipenv install --dev nb-clean`. `nb-clean`
requires Python 3.6 or later.

## Usage

### Cleaning

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

`nb-clean` will configure a filter in the Git repository in which it is run, and
won't mutate your global or system Git configuration. To remove the filter, run:

```bash
nb-clean remove-filter
```

Aside from usage from a filter in a Git repository, you can also clean up a
Jupyter notebook with:

```bash
nb-clean clean notebook.ipynb
```

This cleans the notebook in place. You can also pass the notebook content on
standard input, in which case the cleaned notebook is written to standard
output:

```bash
nb-clean clean < original.ipynb > cleaned.ipynb
```

To also remove empty cells, add the `-e`/`--remove-empty-cells` flag. To
preserve cell metadata, add the `-m`/`--preserve-cell-metadata` flag.

### Checking

You can check if a notebook is clean with:

```bash
nb-clean check notebook.ipynb
```

or by passing the notebook contents on standard input:

```bash
nb-clean check < notebook.ipynb
```

To also check for empty cells, add the `-e`/`--remove-empty-cells` flag. To
ignore cell metadata, add the `-m`/`--preserve-cell-metadata` flag.

`nb-clean` will exit with status code 0 if the notebook is clean, and status
code 1 if it is not. `nb-clean` will also print details of cell execution
counts, metadata, outputs, and empty cells it finds.

### Migrating to `nb-clean` 2

The following table maps from the command line interface of `nb-clean` 1.6.0 to
that of `nb-clean` 2.0.0.

| Description                             | `nb-clean` 1.6.0                                                    | `nb-clean` 2.0.0                                            |
| --------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------- |
| Clean notebook                          | `nb-clean clean -i/--input notebook.ipynb \| sponge notebook.ipynb` | `nb-clean clean notebook.ipynb`                             |
| Clean notebook (remove empty cells)     | `nb-clean clean -i/--input notebook.ipynb -e/--remove-empty`        | `nb-clean clean -e/--remove-empty-cells notebook.ipynb`     |
| Clean notebook (preserve cell metadata) | `nb-clean clean -i/--input notebook.ipynb -m/--preserve-metadata`   | `nb-clean clean -m/--preserve-cell-metadata notebook.ipynb` |
| Check notebook                          | `nb-clean check -i/--input notebook.ipynb`                          | `nb-clean check notebook.ipynb`                             |
| Check notebook (remove empty cells)     | `nb-clean check -i/--input notebook.ipynb -e/--remove-empty`        | `nb-clean check -e/--remove-empty-cells notebook.ipynb`     |
| Check notebook (preserve cell metadata) | `nb-clean check -i/--input notebook.ipynb -m/--preserve-metadata`   | `nb-clean check -m/--preserve-cell-metadata notebook.ipynb` |
| Add Git filter to clean notebooks       | `nb-clean configure-git`                                            | `nb-clean add-filter`                                       |
| Remove Git filter                       | `nb-clean unconfigure-git`                                          | `nb-clean remove-filter`                                    |

## Copyright

Copyright © 2017-2020 [Scott Stevenson].

`nb-clean` is distributed under the terms of the [ISC licence].

[isc licence]: https://opensource.org/licenses/ISC
[papermill]: https://papermill.readthedocs.io/
[pip]: https://pip.pypa.io/
[pipenv]: https://pipenv.readthedocs.io/
[poetry]: https://python-poetry.org/
[pypi]: https://pypi.org/project/nb-clean/
[scott stevenson]: https://scott.stevenson.io
