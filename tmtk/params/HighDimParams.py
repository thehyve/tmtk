from tmtk.params import ParamsBase
import tmtk.utils as utils
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
                    'possible_values': ['R'],
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
                    'helptext': ('If present must be 2. The log base for '
                                 'calculating log values.')
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
                                 'when the data set doesn\'t provide data for all '
                                 'the annotations (here ')
                                       },
                }

    def is_viable(self):
        """

        :return: True if both the datafile and map file are located, else returns False.
        """
        if self.__dict__.get('DATA_FILE', None) and self.__dict__.get('MAP_FILENAME', None):
            datafile_found = os.path.exists(os.path.join(self.dirname, self.DATA_FILE))
            mapfile_found = os.path.exists(os.path.join(self.dirname, self.MAP_FILENAME))
            return all([datafile_found, mapfile_found])
        else:
            return False
