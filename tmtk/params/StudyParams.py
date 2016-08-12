from .ParamsBase import ParamsBase


class StudyParams(ParamsBase):
    docslink = "https://github.com/thehyve/transmart-batch/blob/master/docs/study-params.md"

    @property
    def mandatory(self):
        return {'STUDY_ID': {
            'default': ('Uppercased parent directory name of the params'
                        ' file is default.'),
            'helptext': 'Identifier of the study.',
        }
        }

    @property
    def optional(self):
        return {"TOP_NODE": {
            'default': '\(Public|Private) Studies\<STUDY_ID>',
            'helptext': 'The study top node.'
        },
            "SECURITY_REQUIRED": {
                'possible_values': ['Y', 'N'],
                'default': 'N',
                'helptext': ('Defines study as Private (Y) or Public (N).')
            },
        }

    def is_viable(self):
        """

        :return: True if STUDY_ID has been set.
        """
        if self.get('STUDY_ID', None):
            return True
        else:
            return False
