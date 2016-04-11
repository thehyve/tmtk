from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class HighDimParams(ParamsBase):
    def validate(self, verbosity=2):
        """
        Validate this parameter file.
        :param verbosity:
        :return:
        """

        mandatory = ['DATA_FILE',
                     'DATA_TYPE',
                     'MAP_FILENAME',
                     ]
        optional = ['LOG_BASE',
                    'ALLOW_MISSING_ANNOTATIONS'
                    ]

        message = self._check_for_correct_params(mandatory, optional)
        return self._process_validation_message(message)

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
