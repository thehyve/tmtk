from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class ClinicalParams(ParamsBase):

    @property
    def mandatory(self):
        return ['COLUMN_MAP_FILE']

    @property
    def optional(self):
        return ['WORD_MAP_FILE', 'XTRIAL_FILE', 'TAGS_FILE']

    def is_viable(self):
        """

        :return: True if both the column mapping file is located, else returns False.
        """
        if self.__dict__.get('COLUMN_MAP_FILE', None):
            file_found = os.path.exists(os.path.join(self.dirname, self.COLUMN_MAP_FILE))
            return file_found
        else:
            return False
