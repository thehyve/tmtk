from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class ClinicalParams(ParamsBase):
    def validate(self, verbosity=2):
        """
        Validate this parameter file.
        :param verbosity:
        :return:
        """

        mandatory = ['COLUMN_MAP_FILE',
                     ]
        optional = ['WORD_MAP_FILE',
                    'XTRIAL_FILE',
                    'TAGS_FILE',
                    ]

        message = self._check_for_correct_params(mandatory, optional)
        return self._process_validation_message(message)

    def is_viable(self):
        """

        :return: True if both the column mapping file is located, else returns False.
        """
        if self.__dict__.get('COLUMN_MAP_FILE', None):
            file_found = os.path.exists(os.path.join(self.dirname, self.COLUMN_MAP_FILE))
            return file_found
        else:
            return False
