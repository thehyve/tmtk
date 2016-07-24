import os
import pandas as pd

from ..arborist import call_boris
from ..utils import FileBase, Exceptions, Mappings, path_converter, path_join
from ..params import ClinicalParams


class ColumnMapping(FileBase):
    """
    Class with utilities for the column mapping file for clinical data.
    Can be initiated with either a path to column mapping file, or a clinical params file object.
    """
    def __init__(self, params=None):

        self.params = params

        if not isinstance(params, ClinicalParams):
            raise Exceptions.ClassError(type(params))
        elif params.__dict__.get('COLUMN_MAP_FILE'):
            self.path = os.path.join(params.dirname, params.COLUMN_MAP_FILE)
        else:
            self.path = os.path.join(params.dirname, 'column_mapping_file.txt')
            self.params.__dict__['COLUMN_MAP_FILE'] = os.path.basename(self.path)
        super().__init__()

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

    @staticmethod
    def create_df():
        df = pd.DataFrame(dtype=str, columns=Mappings.column_mapping_header)
        return df

    def call_boris(self):
        self.df = call_boris(self.df)

    def validate(self, verbosity=2):
        pass

    def select_row(self, var_id):
        filename, column = var_id.rsplit('__', 1)
        f = self.df.ix[:, 0].astype(str) == filename
        c = self.df.ix[:, 2].astype(str) == column
        if sum(f & c) > 1:
            raise Exceptions.TooManyValues(sum(f & c), 1, var_id)
        row = self.df.ix[f & c]
        return list(row.values[0, :])

    def get_concept_path(self, var_id):
        row = self.select_row(var_id)
        cp = path_join(row[1], row[3])
        return path_converter(cp)

    @staticmethod
    def _df_mods(df):
        """
        df_mods applies modifications to the dataframe before it is cached.
        :return:
        """
        df.fillna("", inplace=True)
        return df
