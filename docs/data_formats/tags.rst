=============================
Metadata tags and description
=============================

The metadata which will appear in a popup in the tree of tranSMART. Can be used to add additional information to your concepts.

File structure
--------------

::

    study_directory
    └── tags
        ├── tags.params
        └── tags.txt


Parameter file
--------------

The parameters file should be named ``tags.params`` and contains:

* ``TAGS_FILE`` **Mandatory**. Points to the tags file. See below for format.

File format
-----------

The metadata files are expected a flat tab seperated text file with **four** columns:

* ``Concept path``. Indicate to which concept the metadata belongs. Metadata on the study level is indicated with a '\\\\'
* ``Tag title``. Title of the metadata to be displayed
* ``Tag description``. Description of the field
* ``Weight``. Determines order of the metadata in transmart, the higher the number the lower the tag will appear

Example input file:

+----------------+--------------+---------------------+---------+
| concept path   | tag title    | tag description     | Weight  |
+================+==============+=====================+=========+
|\\              | ORGANISM     | Homo Sapiens        |   2     |
+----------------+--------------+---------------------+---------+
|\\Subjects\\Age | Info         | At time of diagnosis|   3     |
+----------------+--------------+---------------------+---------+


**NOTE**: The header row is **mandatory**, the column order is set but the column names are flexible.