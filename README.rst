====
tmtk
====

Master:

.. image:: https://travis-ci.org/thehyve/tmtk.svg?branch=master
    :target: https://travis-ci.org/thehyve/tmtk

.. image:: https://codecov.io/gh/thehyve/tmtk/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/thehyve/tmtk

.. image:: https://readthedocs.org/projects/tmtk/badge/?version=latest
    :target: http://tmtk.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Develop:

.. image:: https://travis-ci.org/thehyve/tmtk.svg?branch=develop
    :target: https://travis-ci.org/thehyve/tmtk

.. image:: https://codecov.io/gh/thehyve/tmtk/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/thehyve/tmtk


Anaconda Cloud latest package:

.. image:: https://anaconda.org/conda-forge/tmtk/badges/version.svg
    :target: https://anaconda.org/conda-forge/tmtk


A toolkit for ETL curation for the tranSMART data warehouse. The
TranSMART curation toolkit (``tmtk``) can be used to edit and validate
studies prior to loading them with `transmart-batch`_.

For general documentation visit `readthedocs`_.

Installation
------------

Installing via Anaconda Cloud or Pip package managers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Anaconda:

.. code:: sh

    conda install -c conda-forge tmtk

Pip:

.. code:: sh

    pip install tmtk

Installing manually
^^^^^^^^^^^^^^^^^^^

Initialize a virtualenv
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    python3 -m venv env
    source env/bin/activate


Installation from source
~~~~~~~~~~~~~~~~~~~~~~~~

To install *tmtk* and all dependencies into your Python environment,
and enable the Arborist Jupyter notebook extension, run:

.. code:: sh

    pip install -r requirements.txt
    python setup.py install

or if you want to run the tool from code in development mode:

.. code:: sh

    pip install -r requirements.txt
    python setup.py develop
    jupyter-nbextension install --py tmtk.arborist
    jupyter-serverextension enable tmtk.arborist


Requirements
^^^^^^^^^^^^

The dependencies are in ``requirements.txt``,
optional dependencies are in ``requirements-dev.txt``.


Licence
-------

LGPL-3.0

.. _transmart-batch: https://github.com/thehyve/transmart-batch/
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io
.. _readthedocs: https://tmtk.readthedocs.io/en/latest/
.. _examples: examples
