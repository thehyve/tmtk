==============
Data templates
==============

This document describes how you can use tmtk to read your filled in templates
and write the data to tranSMART-ready files. The templates can be downloaded `here <https://drive.google.com/open?id=0B5m3DYILzHFKeVEyZFU2RVFuYm8>`_.

Create study templates
----------------------

Using the ``tmtk.toolbox.create_study_from_templates()`` function you
can process any template you have filled in, and output the contents
to a format that can be uploaded to tranSMART. It has the following parameters:

- ``ID`` **(Mandatory)** Unique identifier of the study. This argument does not define the name of the study, that will be derived from ``Level 1`` of the clinical data template tree sheet.
- ``source_dir`` **(Mandatory)** Path to the folder in which the filled in templates are stored. Template files are not searched recursively, so all should be in the same folder.
- ``output_dir`` Path to the folder where the tranSMART files should we written to. If the path doesn't exist the required folder(s) will be created. Default: ``./<STUDY_ID>_transmart_files``
- ``sec_req`` Determines whether it should be a public or private study. Use ``Y`` for private or ``N`` for public. Default: ``Y``

It is important that your ``source_dir`` contains just one clinical data template, which is detected
by having "clinical" somewhere in the file name (case insensitive). If the template with general
study level metadata is present it should have "general study metadata" in its name (case insensitive).
All high-dimensional templates are detected by content, so file names are not important, as long as the
names don't conflict with the templates described above.

**Note:** It is possible to run the function with only high-dimensional templates, but keep in mind that
in that case the concept paths will have to be manually added to the subject-sample mapping files.


.. code:: python

    # Load the toolkit
    import tmtk

.. code:: python

    # Read templates and write to tranSMART files
    tmtk.toolbox.create_study_from_templates(ID='MY-TEMPLATE-STUDY',
                                             source_dir='./my_templates_folder/',
                                             sec_req='N')
