nb-clean
========

.. image:: https://img.shields.io/travis/srstevenson/nb-clean.svg?maxAge=2592000
	   :target: https://travis-ci.org/srstevenson/nb-clean

.. image:: https://img.shields.io/github/tag/srstevenson/nb-clean.svg?maxAge=2592000
	   :target: https://github.com/srstevenson/nb-clean/releases

.. image:: https://img.shields.io/pypi/v/nb-clean.svg?maxAge=2592000
	   :target: https://pypi.python.org/pypi/nb-clean/

``nb-clean`` cleans Jupyter notebooks of cell execution counts and outputs,
preparing them for committing to version control. It provides a Git filter to
automatically clean notebooks before they are staged, and can also be used as a
standalone tool outside Git or with other version control systems.

Installation
------------

To install the latest release from `PyPI`_, use `pip`_:

.. code-block:: bash

    pip install nb-clean

``nb-clean`` requires Python 3.6 or later.

.. _`pip`: https://pip.pypa.io/
.. _`PyPI`: https://pypi.python.org/pypi/nb-clean

Usage
-----

To install a filter in an existing Git repository to automatically clean
notebooks before they are staged, run the following from the working tree:

.. code-block:: bash

    nb-clean configure-git

``nb-clean`` will configure a filter in the Git repository in which it is run,
and will not mutate your global or system Git configuration. To remove the
filter, run:

.. code-block:: bash

    nb-clean unconfigure-git

Aside from usage from a filter in a Git repository, you can also clean up a
Jupyter notebook manually with:

.. code-block:: bash

    nb-clean clean -i original.ipynb -o clean.ipynb

Copyright
---------

Copyright © 2017-2018 `Scott Stevenson`_.

``nb-clean`` is distributed under the terms of the `ISC licence`_.

.. _`ISC licence`: https://opensource.org/licenses/ISC
.. _`Scott Stevenson`: https://scott.stevenson.io
