import tmtk.utils as utils


class DataFile(utils.FileBase):
    """
    Class for clinical data files, does not do much more than tmkt.FileBase.
    """

    def __init__(self, path=None):
        """
        Initialize this class by specifying a path to the data file.

        :param path: path to datafile.
        """
        self.path = path
        super().__init__()

