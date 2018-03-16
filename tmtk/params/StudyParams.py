from .base import ParamsBase

import os
import json


class StudyParams(ParamsBase):
    docslink = "https://github.com/thehyve/transmart-batch/blob/master/docs/study-params.md"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_blob = None

    @property
    def mandatory(self):
        return {
            'STUDY_ID': {
                'default': ('Uppercased parent directory name of the params'
                            ' file is default.'),
                'helptext': 'Identifier of the study.',
            }
        }

    @property
    def optional(self):
        return {
            "TOP_NODE": {
                'default': '\(Public|Private) Studies\<STUDY_ID>',
                'helptext': 'The study top node.'
            },
            "SECURITY_REQUIRED": {
                'possible_values': ['Y', 'N'],
                'default': 'Y',
                'helptext': 'Defines study as Private (Y) or Public (N).'
            },
            "STUDY_JSON_BLOB": {
                'helptext': 'Points to JSON file that will be loaded as study blob.'
            }
        }

    def write_to(self, path, *args, **kwargs):

        super().write_to(path, *args, **kwargs)

        blob_param = self.get('STUDY_JSON_BLOB')
        if self.json_blob and blob_param:

            with open(os.path.join(os.path.dirname(path), blob_param), 'w') as f:
                json.dump(self.json_blob, f)


