from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class TagsParams(ParamsBase):

    @property
    def mandatory(self):
        return ['TAGS_FILE']

    @property
    def optional(self):
        return []

    def is_viable(self):
        """

        :return: True if both the column mapping file is located, else returns False.
        """
        if self.__dict__.get('TAGS_FILE', None):
            file_found = os.path.exists(os.path.join(self.dirname, self.TAGS_FILE))
            return file_found
        else:
            return False

