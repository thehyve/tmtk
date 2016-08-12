from .ParamsBase import ParamsBase
import os


class HighDimParams(ParamsBase):
    docslink = "https://github.com/thehyve/transmart-batch/blob/master/docs/hd-params.md"

    @property
    def mandatory(self):
        return {'DATA_FILE': {
            'variable_type': 'filename',
            'helptext': 'Points to the HD data file.'
        },
            'DATA_TYPE': {
                'possible_values': ['R', 'L'],
                'default': 'R',
                'helptext': ('Must be R (raw values). Other types are not '
                             'supported yet.')
            },
            "MAP_FILENAME": {
                'variable_type': 'filename',
                'helptext': 'Filename of the mapping file.'
            },
        }

    @property
    def optional(self):
        return {"LOG_BASE": {
            'default': '2',
            'helptext': 'Keep this at 2 (sorry about that).'
        },
            "SRC_LOG_BASE": {
                'default': '2',
                'helptext': ('Has to be specified only with DATA_TYPE=L. '
                             'Specifies which logarithm base was '
                             'used for transforming the data values.')
            },
            "NODE_NAME": {
                'default': '<HD data type name>',
                'helptext': ('What to append to TOP_NODE for form the concept '
                             'path of the HD node (before the part generated '
                             'from category_cd).')
            },
            "ALLOW_MISSING_ANNOTATIONS": {
                'possible_values': ['Y', 'N'],
                'default': 'N',
                'helptext': ('Whether the job should be allowed to continue '
                             'when the data set doesn\'t provide data for all '
                             'the annotations (here probes).')
            },
            "SKIP_UNMAPPED_DATA": {
                'possible_values': ['Y', 'N'],
                'default': 'N',
                'helptext': ('Allow data in data file that has no associated '
                             'samples in subject sample mapping.')
            },
            "PROB_IS_NOT_1": {
                'possible_values': ['WARN', 'ERROR'],
                'default': 'ERROR',
                'helptext': ('For CNV data probabilities are checked. If sum '
                             'is not equal to 1, raise either error or give  '
                             'a warning.')
            },
        }

    def is_viable(self):
        """

        :return: True if both the datafile and map file are located, else returns False.
        """
        if self.get('DATA_FILE') and self.get('MAP_FILENAME'):
            datafile_found = os.path.exists(os.path.join(self.dirname, self.DATA_FILE))
            mapfile_found = os.path.exists(os.path.join(self.dirname, self.MAP_FILENAME))
            return all([datafile_found, mapfile_found])
        else:
            return False
