from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class HighDimParams(ParamsBase):

    @property
    def mandatory(self):
        return ['DATA_FILE', 'DATA_TYPE', 'MAP_FILENAME']

    @property
    def optional(self):
        return ['LOG_BASE', 'ALLOW_MISSING_ANNOTATIONS', 'SKIP_UNMAPPED_DATA']

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
