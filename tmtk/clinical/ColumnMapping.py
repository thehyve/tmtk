import os
import pandas as pd

from ..arborist import call_boris
from ..utils import (FileBase, Exceptions, Mappings, path_converter,
                     path_join, CPrint, column_map_diff)
from ..params import ClinicalParams
from .DataFile import DataFile


class ColumnMapping(FileBase):
    """
    Class with utilities for the column mapping file for clinical data.
    Can be initiated with by giving a clinical params file object.
    """

    def __init__(self, params=None):
        """
        Initialize by giving a parameter object.

        :param params: `ClinicalParams` object.
        """
        self.params = params

        if not isinstance(params, ClinicalParams):
            raise Exceptions.ClassError(type(params))
        elif params.get('COLUMN_MAP_FILE'):
            self.path = os.path.join(params.dirname, params.COLUMN_MAP_FILE)
        else:
            self.path = os.path.join(params.dirname, 'column_mapping_file.txt')
            self.params['COLUMN_MAP_FILE'] = os.path.basename(self.path)
        super().__init__()

        self._initial_paths = self.path_id_dict

    @property
    def included_datafiles(self):
        """List of datafiles included in column mapping file."""
        return list(self.df.ix[:, 0].unique())

    @property
    def ids(self):
        """A list of variable identifier tuples."""
        self.build_index()
        return list(self.df.index)

    def create_df(self):
        """
        Create `pd.DataFrame` with a correct header.

        :return: `pd.DataFrame`.
        """
        df = pd.DataFrame(dtype=str, columns=Mappings.column_mapping_header)
        df = self._df_mods(df)
        df = self.build_index(df)
        return df

    def call_boris(self):
        """
        Use The Arborist to modify only information in the column mapping file.
        """
        self.df = call_boris(self.df)

    def validate(self, verbosity=2):
        pass

    def select_row(self, var_id: tuple):
        """
        Select row based on variable identifier tuple.  Raises exception if
        variable is not in this column mapping.

        :param var_id: tuple of filename and column number.
        :return: list of items in selected row.
        """
        rows = self.df.loc[tuple(var_id)]

        if isinstance(rows, pd.Series):
            return list(rows)
        elif isinstance(rows, pd.DataFrame):
            raise Exceptions.TooManyValues(rows.shape[0], 1, var_id)

    def get_concept_path(self, var_id: tuple):
        """
        Return concept path for given variable identifier tuple.

        :param var_id: tuple of filename and column number.
        :return str: concept path for this variable.
        """
        row = self.select_row(var_id)
        cp = path_join(row[1], row[3])
        return path_converter(cp)

    @staticmethod
    def _df_mods(df):
        """
        _df_mods applies modifications to the dataframe before it is cached.

        :param df: `pd.DataFrame`.
        :return: `pd.DataFrame`.
        """
        df.fillna("", inplace=True)
        df.ix[:, 2] = df.ix[:, 2].astype(int)
        return df

    def build_index(self, df=None):
        """
        Build index for the column mapping dataframe.  If `pd.DataFrame`
        (optional) is given, modify and return that.

        :param df: `pd.DataFrame`.
        :return: `pd.DataFrame`.
        """
        if not isinstance(df, pd.DataFrame):
            df = self.df
        df.set_index(list(df.columns[[0, 2]]), drop=False, inplace=True)
        df.sortlevel(inplace=True)
        return df

    def append_from_datafile(self, datafile):
        """
        Appends the column mapping file with rows based on datafile column names.

        :param datafile: `tmtk.DataFile` object.
        """

        if not isinstance(datafile, DataFile):
            raise TypeError(datafile)

        cols_min_four = [""] * (self.df.shape[1] - 4)
        for i, name in enumerate(datafile.df.columns, 1):
            var_id = (datafile.name, i)
            try:
                self.select_row(var_id)
                CPrint.warn("Skipping {!r}, already in column mapping file.".format(var_id))
            except KeyError:
                self.df.loc[i] = [datafile.name, datafile.name, i, name] + cols_min_four

        self.build_index()

    @property
    def path_id_dict(self):
        """Dictionary with all variable ids as keys and paths as value."""
        return {v: self.get_concept_path(v) for v in self.ids}

    def path_changes(self, silent=False):
        """
        Determine changes made to column mapping file.

        :param silent: if True, only print output.
        :return: if `silent=False` return dictionary with changes since load.
        """
        diff = column_map_diff(self._initial_paths, self.path_id_dict)
        if not silent:
            for var_id, item in diff.items():
                print("{}: {}".format(*var_id))
                print("        {}".format(item[0]))
                print("     -> {}".format(item[1]))
        else:
            return diff
