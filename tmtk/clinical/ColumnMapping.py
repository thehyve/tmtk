import os
import tmtk.utils as utils
import tmtk


class ColumnMapping(object):
    """
    Class with utilities for the column mapping file for clinical data.
    Can be initiated with either a path to column mapping file, or a clinical params file object.
    """
    def __init__(self, params=None):
        if isinstance(params, tmtk.ParamsFile) and params.datatype == 'clinical':
            self.path = os.path.join(params.dirname, params.COLUMN_MAP_FILE)
        else:
            raise utils.exceptions.ClassError(type(params), tmtk.ParamsFile)

        self.df = utils.file2df(self.path)

    def included_datafiles(self):
        return self.df.ix[:, 0].unique()

    def call_boris(self):
        utils.call_boris(self)

    def write_to(self):
        utils.df2file(self)
