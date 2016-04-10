import tmtk.utils as utils


class DataFile:
    """
    Base Class for clinical data files.
    """
    def __init__(self, path=None):
        self.path = path
        self.df = utils.file2df(self.path)

    def find_column_datatype(self):
        utils.find_column_datatype(self.df)

    def validate(self):
        utils.validate_clinical_data(self.df)

    def autofill(self):
        """
        Auto fill ClinicalData file column.
        """
        pass