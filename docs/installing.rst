Installing Arkady
=================

Arkady is still in early development and I have not issued a release on PyPI, so
downloading and installing from source on GitHub is the recommended course of
action currently.

https://github.com/SavinaRoja/arkady

Arkady should be installed with Python of version 3.5 or greater, as this is
when ``asyncio`` was introduced. Arkady makes use of ``asyncio`` internally
for concurrent, non-blocking function. You can write Arkady components to take
advantage of ``asyncio``, but more on that later. All references to ``python``
and ``pip`` in commands are assumed to be for that version or later.

Installation is simple once you have downloaded the source, just navigate to the
base directory of the source code and perform:

.. code-block:: bash

    python setup.py install
::

or

.. code-block:: bash

    pip install .
::

Development Installation
------------------------

If you are looking to experiment with modifying Arkady, you will want to install
it in so-called "development mode" using the ``-e`` flag Creating and working in
a virtual environment is simple and recommended, here it is in bash:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate
    pip install -e .
::

and for Windows:

.. code-block:: console

    python -m venv venv
    .\venv\Scripts\activate
    pip install -e .
::