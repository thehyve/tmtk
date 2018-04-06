===================
Study folder format
===================
When loading a study structure to TMTK a folder format is expected, the same
structure is supported in transmart-batch. 


File structure
--------------

::

    study_directory
    ├── study.params
    │
    ├── clinical
    │	├── clinical.params
    │	├── column_mapping.txt
    │	├── word_mapping.txt
    │	├── modifiers.txt
    │	├── ontology_mapping.txt
    │	├── trial_visits.txt
    │	├── data_file_1.txt
    │	├── ...
    │	└── data_file_X.txt
    │
    ├── expression
    │	├── annotation
    │	│	├── mrna_annotation.params
    │	│	└── mrna_annotation_file.txt
    │	├── mrna.params
    │	├── subject_sample_mapping.txt
    │	└── expression_data_file.txt
    │
    ├── ...
    │
    ├── rnaseq
    │	├── annotation
    │	│	├── rnaseq_annotation.params
    │	│	└── rnaseq_annotation_file.txt
    │	├── rnaseq.params
    │	├── subject_sample_mapping.txt
    │	└── rnaseq_data_file.txt
    │
    └── tags
        ├── tags.params
        └── tags.txt


Study parameters
----------------

A parameter file in which the study wide parameters are stored like the
study identifier and whether a study needs to be securly loaded.

- ``STUDY_ID`` **Mandatory** Identifier of the study.
- ``SECURITY_REQUIRED`` _Default:_ `Y`. Defines study as Private (`Y`) or Public (`N`).
- ``TOP_NODE`` The study top node. Has to start with '\\' (e.g. '\\Public Studies\\Cell-lines'). *Default:* '\\(Public|Private) Studies\\<STUDY_ID>'. 
