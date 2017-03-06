.. tmtk documentation master file, created by
   sphinx-quickstart on Mon Aug  8 13:51:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

`tmtk` - TranSMART data curation toolkit
========================================

.. module:: tmkt
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


.. _transmart-batch: https://github.com/thehyve/transmart-batch/
.. _mygene.info: http://mygene.info/

Contents
========
.. toctree::
    :maxdepth: 2

    usage
    api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
