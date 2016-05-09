import os
import tmtk.utils as utils
import tmtk


class ColumnMapping:
    """
    Class with utilities for the column mapping file for clinical data.
    Can be initiated with either a path to column mapping file, or a clinical params file object.
    """
    def __init__(self, params=None):
        if params and params.is_viable() and params.datatype == 'clinical':
            self.path = os.path.join(params.dirname, params.COLUMN_MAP_FILE)
        else:
            raise utils.Exceptions.ClassError(type(params), tmtk.ClinicalParams)

        self.df = utils.file2df(self.path)

    @property
    def included_datafiles(self):
        """
        List of datafiles included in column mapping file.
        :return: list.
        """
        return list(self.df.ix[:, 0].unique())

    def call_boris(self):
        self.df = utils.call_boris(self.df)

    def write_to(self):
        utils.df2file(self)

    def validate(self, verbosity=2):
        pass
