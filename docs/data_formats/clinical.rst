=============
Clinical Data
=============

Clinical data is meant for all kind of measurements not falling into
other categories. It can be data from questionnaires, physical body
measurements or socio-economic info about patient.


File structure
--------------

::

    study_directory
    └── clinical
        ├── clinical.params
        ├── column_mapping.txt
        ├── word_mapping.txt
        ├── modifiers.txt
        ├── ontologies.txt
        ├── trial_visits.txt
        ├── data_file_1.txt
        ├── ...
        └── data_file_X.txt


Parameter file
--------------

* ``COLUMN_MAP_FILE``. **Mandatory**. Points to the column mapping file.
* ``WORD_MAP_FILE``. Points to the file with dictionary to be used.
* ``MODIFIERS``. Points to the modifier file of the study. Only needed when using modifiers
* ``ONTOLOGY_MAP_FILE``. Points to the ontology mapping for this study. Only needed when using ontologies
* ``TRIAL_VISITS_FILE``. Points to the trial visits file for this study. Only needed when using trial_visits


File formats
------------

Column mapping file format
''''''''''''''''''''''''''
A tab separated file with **seven** columns:

* ``Filename``. Filename of the data file refering to the data
* ``Category Cd``. Concept path to be displayed in tranSMART
* ``Column number``. Column number from the data file
* ``Data Label``. Data label to display in tranSMART
* ``Reference column``. Column to which the data from this column will refer to
* ``Ontology code``. Ontology code from the **ontology mapping file**
* ``Concept Type``. Type of the concept, see *Allowed values for Concept type* for more information

Example column mapping file:

+--------+-----------+---+-----------+---+--------+-------------+
|Filename|Category Cd|Col|Data Label |Ref|Ontology|Concept Type |
|        |           |Num|           |Col|code    |             |
+========+===========+===+===========+===+========+=============+
|data.txt|Subjects   |1  |  SUBJ_ID  |   |        |             |
+--------+-----------+---+-----------+---+--------+-------------+
|data.txt|Subjects   |2  |  Age      |   |        |  NUMERICAL  |
+--------+-----------+---+-----------+---+--------+-------------+
|data.txt|Subjects   |3  |  Gender   |   |        |  CATEGORICAL|
+--------+-----------+---+-----------+---+--------+-------------+
|data.txt|Subjects   |4  |  Drug     |   |        |  CATEGORICAL|
+--------+-----------+---+-----------+---+--------+-------------+
|data.txt|Subjects   |5  |  MODIFIER |4  |        |  DOSE       |
+--------+-----------+---+-----------+---+--------+-------------+
|data.txt|Subjects   |6  |  MODIFIER |   |        |  SAMPLE_ID  |
+--------+-----------+---+-----------+---+--------+-------------+
|data.txt|           |7  |TRIAL_VISIT|   |        |             |
+--------+-----------+---+-----------+---+--------+-------------+
|data.txt|           |8  |START_DATE |   |        |             |
+--------+-----------+---+-----------+---+--------+-------------+

Adding modifiers can be done by indicating **MODIFIER** in the ``Data Label`` column and indicating a ``MODIFIER CODE`` in the ``Concept Type`` column. Adding a column number in the ``Reference column`` assigns a modifier to the observations from the reference column. Note that you can indicate multiple references by adding a comma (,) seperated list. Leaving the ``Reference column`` empty means the modifier will be applied to all columns from that data file.

Trial visits, start and end dates are all applied row wide and do not require references. The start and end date do expect a set date format (see Reserved keywords). The value entered for a trial visit in the data file should also be defined in the ``TRIAL_VISIT_FILE`` with the same label.

Reserved keywords for ``Data label``:

* ``SUBJ_ID``. Needs to be indicated once per data file
* ``MODIFIER``. Requires a **modifier code** from the **modifier table** to be inserted in the ``Concept Type`` column
* ``TRIAL_VISIT``. Values from the data file need to be specified in the ``TRIAL_VISIT_FILE``. 
* ``START_DATE``. Required date format: **yyyy-mm-dd hh:mm:ss**
* ``END_DATE``. Required date format: **yyyy-mm-dd hh:mm:ss**

Allowed values for Concept type: 

* ``NUMERICAL``. For numerical data, *default*
* ``CATEGORICAL``. For categorical text values. Can be used to force numerical data to be loaded as categorisch
* ``DATE``. For date values. Expected date format: **yyyy-mm-dd hh:mm:ss**
* ``TEXT``. For free text. Observations are stored as a *BLOB* object and can only be used to select for people who have an observation for this.
* ``MODIFIER CODE``. Codes from the **modifier table**. Any code defined in the **modifier table** can be inserted to indicate which modifier should be linked.


Word mapping file format
''''''''''''''''''''''''
A tab separated file with **four** columns:

* ``Filename``. Filename of the data file refering to the data
* ``Column number``. Column number from the file to which the substitution should be done
* ``From value``. Value to be replaced
* ``To value``. New value

Example word mapping file:

+--------+---+------+------------+
|Filename|Col|From  |To          |
|        |Num|Value |Value       |
+========+===+======+============+
|data.txt|3  | M    |Male        | 
+--------+---+------+------------+
|data.txt|3  | F    |Female      |
+--------+---+------+------------+
|data.txt|4  | ASP  |Aspirin     |
+--------+---+------+------------+
|data.txt|4  | PAC  |Paracetamol |
+--------+---+------+------------+


Trial visit file format
'''''''''''''''''''''''
A tab separated file with **three** columns:

* ``Visit name``. **Mandatory** Name of the visit, displayed in the tranSMART UI
* ``Relative time``. Integer indicating the length of time
* ``Time unit``. Unit of time, possible values: Days, Weeks, Months, Years

The only mandatory field is the ``Visit name``.

Example trial visit file:

+-------------+-------------+---------+
|Visit name   |Relative time|Time unit|
+=============+=============+=========+
|Baseline     |0            |Months   |
+-------------+-------------+---------+ 
|Treatment    |3            |Months   |
+-------------+-------------+---------+ 
|Follow up    |6            |Months   |
+-------------+-------------+---------+ 
|Preoperative |             |         |
+-------------+-------------+---------+ 
|Postoperative|             |         |
+-------------+-------------+---------+ 


Modifier file format
''''''''''''''''''''
A tab separated file with **four** columns:

* ``Modifier path``. Path of the modifier.
* ``Modifier code``. Unique modifier code. Used in the **column mapping file** as ``Concept type``
* ``Name charater``. Label of the modifier
* ``Data type``. Data type of the modifier, options *CATEGORICAL* or *NUMERICAL*

+---------+---------+------------------------+-----------+
|modifier |modifier |name                    |data       |
|path     |code     |char                    |type       |
+=========+=========+========================+===========+
|\\Dose   |DOSE     | Drug dose administered |NUMERICAL  |
+---------+---------+------------------------+-----------+
|\\Samples|SAMPLE_ID| Modifier for Samples   |CATEGORICAL|
+---------+---------+------------------------+-----------+ 


Ontology file format
''''''''''''''''''''

To be implemented




