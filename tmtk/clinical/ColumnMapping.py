import os
import tmtk
from tmtk import arborist, utils


class ColumnMapping:
    """
    Class with utilities for the column mapping file for clinical data.
    Can be initiated with either a path to column mapping file, or a clinical params file object.
    """
    def __init__(self, params=None):
        if params and params.is_viable() and params.datatype == 'clinical':
            self.path = os.path.join(params.dirname, params.COLUMN_MAP_FILE)
        else:
            raise utils.Exceptions.ClassError(type(params), tmtk.params.ClinicalParams)

    @utils.cached_property
    def df(self):
        return utils.file2df(self.path)

    @property
    def included_datafiles(self):
        """
        List of datafiles included in column mapping file.
        :return: list.
        """
        return list(self.df.ix[:, 0].unique())

    @property
    def ids(self):
        return self.df.apply(lambda x: '{}__{}'.format(x[0], x[2]), axis=1)

    def call_boris(self):
        self.df = arborist.call_boris(self.df)

    def write_to(self):
        utils.df2file(self)

    def validate(self, verbosity=2):
        pass

    def select_row(self, var_id):
        filename, column = var_id.rsplit('__', 1)
        f = self.df.ix[:, 0].astype(str) == filename
        c = self.df.ix[:, 2].astype(str) == column
        if sum(f & c) > 1:
            raise utils.TooManyValues(sum(f & c), 1, var_id)
        row = self.df.ix[f & c]
        return list(row.values[0, :])

    def get_concept_path(self, var_id):
        row = self.select_row(var_id)
        return '{}+{}'.format(row[1], row[3])
