.. tmtk documentation master file, created by
   sphinx-quickstart on Mon Aug  8 13:51:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

`tmtk` - TranSMART data curation toolkit
========================================

.. module:: tmtk
.. moduleauthor:: Jochem Bijlard

:Author: Jochem Bijlard
:Source Code: https://github.com/thehyve/tmtk/
:Generated: |today|
:License: GPLv3
:Version: |version|


.. topic:: Philosophy

   A toolkit for ETL curation for the tranSMART data warehouse for
   translational research.

   The TranSMART curation toolkit (``tmtk``) aims to provide a language
   and set of classes for describing data to be uploaded to tranSMART.
   The toolkit can be used to edit and validate studies prior
   to loading them with `transmart-batch`_.

   Functionality currently available:
    * create a transmart-batch ready study from clinical data files.
    * load an existing study and validate its contents.
    * edit the transmart concept tree in The Arborist graphical editor.
    * create chromosomal region annotation files.
    * map HGNC gene symbols to corresponding Entrez gene IDs using `mygene.info`_.


.. note::

   tmtk is a ``python3`` package meant to be run in ``Jupyter notebooks``. Results
   for other setups may vary.


Basic Usage
===========

Step 1: Opening a notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^

First open a Jupyter Notebook, open a shell and change directory to some
place where your data is. Then start the notebook server:

.. code:: sh

    cd /path/to/studies/
    jupyter notebook

This should open your browser to Jupyters file browser, create a new
notebook for here.

Step 2: Using tmtk
^^^^^^^^^^^^^^^^^^

.. code:: py

    # First import the toolkit into your environment
    import tmtk

    # Then create a <tmtk.Study> object by pointing to study.params of a transmart-batch study
    study = tmtk.Study('~/studies/a_tm_batch_ready_study/study.params')
    # Or, by using the study wizard on a directory with correctly structured, clinical data files.
    # (Visit the transmart-batch documentation to find out what is expected.)
    study = tmtk.wizard.create_study('~/studies/dir_with_some_clinical_data_files/')

Now we have loaded the study as a ``tmtk.Study`` object we have some
interesting functions available:

.. code:: py

    # Check whether transmart-batch will find any issues with the way your study is setup
    study.validate_all()

    # Graphically manipulate the concept tree in this study by using The Arborist
    study.call_boris()



Contents
========
.. toctree::
    :maxdepth: 2

    changelog
    usage
    api
    data_templates


Contributors
============

    - Stefan Payrable
    - Ward Weistra

.. _transmart-batch: https://github.com/thehyve/transmart-batch/
.. _mygene.info: http://mygene.info/

