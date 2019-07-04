=========
Changelog
=========


.. topic::  Version 0.5.6

    * Add dimension_type and sort_order columns to the dimension_description
    * Add end dates to the observation_fact export in skinny loader (end date dimension still missing)

.. topic::  Version 0.5.5

    * 16.2 template validation
    * Allow reuse of column names in separate source files used by template reader
    * Template reader source data can be provided in single sheet Excel files

.. topic::  Version 0.5.4

    * Create transmart-copy files without setting ``FAS`` on study node.

.. topic::  Version 0.5.2

    * You can now create a template from an existing tree in BaaS
    * file2df() now reads floats as is

.. topic::  Version 0.5.0

    * Support for Date observations with value type 'D'
    * Fixed issue with lower case top node in deprecated template reader

.. topic::  Version 0.4.4

    * Support for Excel templates for 17.1+
    * Added data density for the random study generator
    * Added package wide options under tmtk.options
    * Added builds for Anaconda
    * Automated testing on Windows

.. topic::  Version 0.4.2

    * Fixed call_boris and related tests and examples.

.. topic::  Version 0.4.1

    * Data types and modifiers support in blueprint.
    * Fixed issue with empty date columns
    * Export studies without including a top node
    * Better support for modifiers other than MISSVAL

.. topic::  Version 0.4.0

    * Added support to export to skinny format (toolbox.SkinnyExport)
    * Support for modifiers and ontology concepts
        * known issue: the Arborist does not have full support yet.
    * Variable objects are more powerful with more setters.

.. topic::  Version 0.3.5

    * Better support for building pipelines from code books using Blueprints
    * Set data label, concept path, and word mapping from clinical variable abstraction
    * Arborist support for _ and +
    * Improved stability of Arborist
    * Fixes in Validator for word map file

.. topic::  Version 0.3.3

    * More easily extensible validator functionality
    * Added multiple validation methods
    * Fix issue with namespace cleaner

.. topic::  Version 0.3.1

    * Replaced deprecated pandas functionality
    * More reliably start batch job

.. topic::  Version 0.3.0

    * Create studies from TraIT data templates, see :ref:`data_templates`.
    * Create fully randomized studies of any size: ``tmtk.toolbox.RandomStudy``.
    * Load data right from Jupyter using transmart-batch, with progress bars!! Also works in
      as a command line tool ``transmart-batch``.
    * Set name and id from the main study object.

.. topic::  Version 0.2.2

    * Minor bug fix for Arborist installation

.. topic::  Version 0.2.1

    * The Arborist is now implemented as a Jupyter Notebook extension
    * Metadata tags are automatically sorted in Arborist.

.. topic::  Version 0.2.0

    * Create and apply tree templates in Arborist
    * Improved interaction with metadata tags in Arborist
    * Resolved issues with the validator
    * R is now an optional dependency
