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


.. _column_mapping_file_format:

Column mapping file
'''''''''''''''''''
A tab separated file with **seven** columns:

* ``Filename``. Filename of the data file refering to the data
* ``Category Cd``. Concept path to be displayed in tranSMART
* ``Column number``. Column number from the data file
* ``Data Label``. Data label to display in tranSMART
* ``Reference column``. Column to which the data from this column will refer to, used by modifiers. Can be a comma (,) separated list to indicate a range of columns.
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

.. _column_mapping_modifiers:

Adding modifiers can be done by indicating **MODIFIER** in the ``Data Label`` column and indicating a ``MODIFIER CODE`` in the ``Concept Type`` column. Adding a column number in the ``Reference column`` assigns a modifier to the observations from the reference column. Note that you can indicate multiple references by adding a comma (,) seperated list. Leaving the ``Reference column`` empty means the modifier will be applied to all columns from that data file.

Trial visits, start and end dates are all applied row wide and do not require references. The start and end date do expect a set date format (see Reserved keywords). The value entered for a trial visit in the data file should also be defined in the ``TRIAL_VISIT_FILE`` with the same label.

Reserved keywords for ``Data label``:

* ``SUBJ_ID``. Needs to be indicated once per data file
* ``MODIFIER``. Requires a **modifier code** from the **modifier table** to be inserted in the ``Concept Type`` column
* ``TRIAL_VISIT``. Values from the data file need to be specified in the ``TRIAL_VISIT_FILE``. 
* ``START_DATE``. Required date format: **yyyy-mm-dd hh:mm:ss**
* ``END_DATE``. Required date format: **yyyy-mm-dd hh:mm:ss**

Allowed values for ``Concept type``: 

* ``NUMERICAL``. For numerical data, *default*
* ``CATEGORICAL``. For categorical text values. Can be used to force numerical data to be loaded as categorisch
* ``DATE``. For date values. Expected date format: **yyyy-mm-dd hh:mm:ss**
* ``TEXT``. For free text. Observations are stored as a *BLOB* object and can only be used to select for people who have an observation for this.
* ``MODIFIER CODE``. Codes from the **modifier table**. Any code defined in the **modifier table** can be inserted to indicate which modifier should be linked.


.. _word_mapping_file_format:

Word mapping file
'''''''''''''''''
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


.. _trial_visit_file_format:

Trial visit file
''''''''''''''''
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


.. _modifier_file_format:

Modifier file
'''''''''''''
A tab separated file with **six** columns:

* ``Modifier path``. Path of the modifier.
* ``Modifier code``. Unique modifier code. Used in the **column mapping file** as ``Concept type``
* ``Name charater``. Label of the modifier
* ``Data Type``. Data type of the modifier, options *CATEGORICAL* or *NUMERICAL*
* ``dimension_type``. Indicates whether the dimension represents subjects or observation attributes, options *SUBJECT* or *ATTRIBUTE* (optional).
* ``sort_index``. Specifies a relative order between dimensions (optional).

+---------+---------+------------------------+-----------+---------+-----+
|modifier |modifier |name                    |data       |dimension|sort |
|path     |code     |char                    |type       |type     |index|
+=========+=========+========================+===========+=========+=====+
|\\Dose   |DOSE     | Drug dose administered |NUMERICAL  | SUBJECT | 2   |
+---------+---------+------------------------+-----------+---------+-----+
|\\Samples|SAMPLE_ID| Modifier for Samples   |CATEGORICAL| SUBJECT | 3   |
+---------+---------+------------------------+-----------+---------+-----+


.. _ontology_file_format:

Ontology file
'''''''''''''

To be implemented


.. _clinical_data_file_format:

Clinical Data file(s)
'''''''''''''''''''''

The clinical data file contains the low-dimensional observations of each
patient. The file name and columns are referenced from the `column
mapping file. Each data file must contain a column
with the patient identifiers.

**Note:** In following examples, each variation on the basic structure
of clinical data files is shown separately for clarity reasons. However,
none of them are mutually exclusive.

Basic structure
~~~~~~~~~~~~~~~

The basic structure of a clinical data file is patients on the rows and
variables on the columns.

+---------------+----------+-----------------+
| Subject\_id   | Gender   | Treatment arm   |
+===============+==========+=================+
| patient1      | Male     | A               |
+---------------+----------+-----------------+
| patient2      | Female   | B               |
+---------------+----------+-----------------+

Adding Observation dates
~~~~~~~~~~~~~~~~~~~~~~~~

When observations are linked to a specific date or time, additional columns for the
**start date** and optionally **end date** can be added. All
observations present in a row with an observation date will be considered to have that observations date.
Start and end date should be provided in YYYY-MM-DD format and may be acompanied by the time of day in HH:MM:SS
format (e.g. 2016-08-23 11:39:00). Please see :ref:`column_mapping_file_format` for information on how to represent this correctly in the column mapping file.

+---------------+--------------+--------------+----------+-----------------+--------+
| Subject\_id   | Start date   | End date     | Gender   | Treatment arm   | BMI    |
+===============+==============+==============+==========+=================+========+
| patient1      |              |              | Male     | A               |        |
+---------------+--------------+--------------+----------+-----------------+--------+
| patient1      | 2016-03-18   | 2016-03-18   |          |                 | 22.7   |
+---------------+--------------+--------------+----------+-----------------+--------+
| patient2      |              |              | Female   | B               |        |
+---------------+--------------+--------------+----------+-----------------+--------+
| patient2      | 2016-03-24   | 2016-03-24   |          |                 | 20.9   |
+---------------+--------------+--------------+----------+-----------------+--------+

Adding Trial visits
~~~~~~~~~~~~~~~~~~~

When one or multiple observations where acquired as part of a clinical
trial, they can be mapped as such by adding a **Trial visit label**
column. All observations in a row will be considered part of the same
trial visit. The trial visit labels should be defined in the trial visit mapping.
See :ref:`trial_visit_file_format` for more information.

+---------------+---------------------+----------+-----------------+--------+--------------+
| Subject\_id   | Trial visit label   | Gender   | Treatment arm   | BMI    | Heart rate   |
+===============+=====================+==========+=================+========+==============+
| patient1      |                     | Male     | A               |        |              |
+---------------+---------------------+----------+-----------------+--------+--------------+
| patient1      | Baseline            |          |                 | 22.7   | 87           |
+---------------+---------------------+----------+-----------------+--------+--------------+
| patient1      | Week 5              |          |                 | 22.6   | 91           |
+---------------+---------------------+----------+-----------------+--------+--------------+
| patient2      |                     | Female   | B               |        |              |
+---------------+---------------------+----------+-----------------+--------+--------------+
| patient2      | Baseline            |          |                 | 20.9   | 82           |
+---------------+---------------------+----------+-----------------+--------+--------------+
| patient2      | Week 5              |          |                 | 20.5   | 82           |
+---------------+---------------------+----------+-----------------+--------+--------------+


Adding Sample-specific data and Custom modifers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Samples are currently recognized by adding modifiers to your observations.
To indicate samples it is recommended to use the ``SAMPLE_ID`` modifier.
The modifier can be added by adding a column with the sample identifiers to the data file. 
When applied, all observations on a row will be linked to the sample identifier.

Next to row-wide modifiers it is also possible to add modifiers for a specific column. These modifiers follow the same
rules as the ``SAMPLE_ID`` modifier apart from the fact they only apply to observations with in the specified columns they are
connected to. 

For an overview on how to add your own custom modifiers and how to represent these in the column mapping file please see:
:ref:`modifier_file_format` and :ref:`column_mapping_file_format`. **Note:** The column mapping file determines if a modifier
is interpreted as row-wide or column specific, see: :ref:`Defining modifiers in the column mapping <column_mapping_modifiers>`.

Example modifier table, *SAMPLE\_ID* and *DOSE* are modifiers:

+---------------+-------------+----------------+---------+------------+-------+
| Subject\_id   |*SAMPLE\_ID* | Hypermutated   | MVD     | Drug       | *DOSE*|
+===============+=============+================+=========+============+=======+
| patient1      | GSM210005   | No             | 51.26   |Paracetamol | 50    |
+---------------+-------------+----------------+---------+------------+-------+
| patient2      | GSM210043   | No             | 27.91   |Aspirin     |  100  |
+---------------+-------------+----------------+---------+------------+-------+
| patient2      | GSM210047   | Yes            | 77.03   | Paracetamol| 500   |
+---------------+-------------+----------------+---------+------------+-------+










