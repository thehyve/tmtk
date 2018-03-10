====
tmtk
====
.. image:: https://travis-ci.org/thehyve/tmtk.svg?branch=master
    :target: https://travis-ci.org/thehyve/tmtk

.. image:: https://codecov.io/gh/thehyve/tmtk/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/thehyve/tmtk

.. image:: https://readthedocs.org/projects/tmtk/badge/?version=latest
    :target: http://tmtk.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


A toolkit for ETL curation for the tranSMART data warehouse. The
TranSMART curation toolkit (``tmtk``) can be used to edit and validate
studies prior to loading them with `transmart-batch`_.

For general documentation visit `readthedocs`_.

Installation
------------

Clone the repo
^^^^^^^^^^^^^^

.. code:: bash

    $ git clone https://github.com/thehyve/tmtk
    $ cd tmtk

Initialize a virtualenv
^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ pip install virtualenv
    $ virtualenv -p /path/to/python3.x/installation env
    $ source env/bin/activate


For mac users it will most likely be

.. code:: bash

    $ pip install virtualenv
    $ virtualenv -p python3 env
    $ source env/bin/activate

or do this using `virtualenvwrapper`_.


Installing
^^^^^^^^^^

To install *tmtk* and all dependencies into your Python environment,
and enable the Arborist Jupyter notebook extension, run:

.. code:: sh

    $   pip3 install tmtk

or..

.. code:: sh

    $   pip3 install -r requirements.txt
    $   python3 setup.py install

or if you want to run the tool from code in development mode:

.. code:: sh

    $   pip3 install -r requirements.txt
    $   python3 setup.py develop
    $   jupyter-nbextension install --py tmtk.arborist
    $   jupyter-serverextension enable tmtk.arborist

Requirements
^^^^^^^^^^^^

These dependencies will have to be installed:
 - pandas>=0.19.2
 - ipython>=5.3.0
 - jupyter>=1.0.0
 - jupyter-client>=5.0.0
 - jupyter-core>=4.3.0
 - jupyter-console>=5.1.0
 - notebook>=4.2.0
 - requests>=2.13.0
 - tqdm>=4.11.0
 - mygene>=3.0.0

Licence
-------

LGPL-3.0

.. _transmart-batch: https://github.com/thehyve/transmart-batch/
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io
.. _readthedocs: https://tmtk.readthedocs.io/en/latest/
.. _examples: examples
