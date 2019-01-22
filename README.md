# nb-clean

`nb-clean` cleans Jupyter notebooks of cell execution counts, metadata, and
outputs, preparing them for committing to version control. It provides a Git
filter to automatically clean notebooks before they are staged, and can also be
used as a standalone tool outside Git or with other version control systems.

## Installation

To install the latest release from [PyPI], use [pip]:

```bash
pip install nb-clean
```

Alternately, in Python projects using [Poetry] or [Pipenv] for dependency
management, add `nb-clean` as a development dependency with
`poetry add --dev nb-clean` or `pipenv install --dev nb-clean`. `nb-clean`
requires Python 3.6 or later.

## Usage

To install a filter in an existing Git repository to automatically clean
notebooks before they are staged, run the following from the working tree:

```bash
nb-clean configure-git
```

`nb-clean` will configure a filter in the Git repository in which it is run, and
will not mutate your global or system Git configuration. To remove the filter,
run:

```bash
nb-clean unconfigure-git
```

Aside from usage from a filter in a Git repository, you can also clean up a
Jupyter notebook manually with:

```bash
nb-clean clean -i original.ipynb -o cleaned.ipynb
```

## Copyright

Copyright © 2017-2019 [Scott Stevenson].

`nb-clean` is distributed under the terms of the [ISC licence].

[isc licence]: https://opensource.org/licenses/ISC
[pip]: https://pip.pypa.io/en/stable/
[pipenv]: https://pipenv.readthedocs.io/en/latest/
[poetry]: https://poetry.eustace.io/
[pypi]: https://pypi.org/project/nb-clean/
[scott stevenson]: https://scott.stevenson.io
