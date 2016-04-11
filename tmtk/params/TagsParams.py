from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class TagsParams(ParamsBase):
    def validate(self, verbosity=2):
        """
        Validate this parameter file.
        :param verbosity:
        :return:
        """

        mandatory = ['TAGS_FILE',
                     ]
        optional = [
                    ]

        message = self._check_for_correct_params(mandatory, optional)
        return self._process_validation_message(message)

    def is_viable(self):
        """

        :return: True if both the column mapping file is located, else returns False.
        """
        if self.__dict__.get('TAGS_FILE', None):
            file_found = os.path.exists(os.path.join(self.dirname, self.TAGS_FILE))
            return file_found
        else:
            return False

