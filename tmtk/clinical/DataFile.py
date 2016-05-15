import tmtk.utils as utils
import os


class DataFile(utils.FileBase):
    """
    Base Class for clinical data files.
    """
    def __init__(self, path=None):
        self.path = path
        self.name = os.path.basename(path)
        super().__init__()

    def validate(self, verbosity=2):
        utils.validate_clinical_data(self.df)

    def autofill(self):
        """
        Auto fill ClinicalData file column.
        """
        pass
