import tmtk.utils as utils
import os


class DataFile:
    """
    Base Class for clinical data files.
    """
    def __init__(self, path=None):
        self.path = path
        self.df = utils.file2df(self.path)
        self.name = os.path.basename(path)

    def validate(self, verbosity=2):
        utils.validate_clinical_data(self.df)

    def autofill(self):
        """
        Auto fill ClinicalData file column.
        """
        pass
