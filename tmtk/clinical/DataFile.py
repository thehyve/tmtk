import tmtk.utils as utils


class DataFile(utils.FileBase):
    """
    Base Class for clinical data files.
    """
    def __init__(self, path=None):
        self.path = path
        super().__init__()

    def validate(self, verbosity=2):
        utils.validate_clinical_data(self.df)

    def autofill(self):
        """
        Auto fill ClinicalData file column.
        """
        pass
