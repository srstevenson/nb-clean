# nb-clean [![Build status](https://img.shields.io/travis/srstevenson/nb-clean.svg?maxAge=2592000)](https://travis-ci.org/srstevenson/nb-clean) [![GitHub tag](https://img.shields.io/github/tag/srstevenson/nb-clean.svg?maxAge=2592000)](https://github.com/srstevenson/nb-clean/releases) [![PyPI release](https://img.shields.io/pypi/v/nb-clean.svg?maxAge=2592000)](https://pypi.org/project/nb-clean/)

`nb-clean` cleans Jupyter notebooks of cell execution counts, metadata, and
outputs, preparing them for committing to version control. It provides a Git
filter to automatically clean notebooks before they are staged, and can also be
used as a standalone tool outside Git or with other version control systems.

## Installation

To install the latest release from [PyPI], use [Pipenv]:

```bash
pipenv install --dev nb-clean
```

`nb-clean` requires Python 3.6 or later.

## Usage

To install a filter in an existing Git repository to automatically clean
notebooks before they are staged, run the following from the working tree:

```bash
nb-clean configure-git
```

`nb-clean` will configure a filter in the Git repository in which it is run,
and will not mutate your global or system Git configuration. To remove the
filter, run:

```bash
nb-clean unconfigure-git
```

Aside from usage from a filter in a Git repository, you can also clean up a
Jupyter notebook manually with:

```bash
nb-clean clean -i original.ipynb -o cleaned.ipynb
```

## Copyright

Copyright © 2017-2018 [Scott Stevenson].

`nb-clean` is distributed under the terms of the [ISC licence].

[ISC licence]: https://opensource.org/licenses/ISC
[Pipenv]: https://docs.pipenv.org/
[PyPI]: https://pypi.org/project/nb-clean/
[Scott Stevenson]: https://scott.stevenson.io
