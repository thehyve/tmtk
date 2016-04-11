from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class AnnotationParams(ParamsBase):
    def validate(self, verbosity=2):
        """
        Validate this parameter file.
        :param verbosity:
        :return:
        """

        mandatory = ['PLATFORM',
                     'TITLE',
                     'ANNOTATIONS_FILE'
                     ]
        optional = ['ORGANISM',
                    'GENOME_RELEASE'
                    ]

        message = self._check_for_correct_params(mandatory, optional)
        return self._process_validation_message(message)

    def is_viable(self):
        """

        :return: True if both the platform is set and the annotations file is located,
        else returns False.
        """
        if self.__dict__.get('ANNOTATIONS_FILE', None) and self.__dict__.get('PLATFORM', None):
            file_found = os.path.exists(os.path.join(self.dirname, self.ANNOTATIONS_FILE))
            return file_found
        else:
            return False
