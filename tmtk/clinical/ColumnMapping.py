import os
import pandas as pd

from ..utils import (FileBase, Exceptions, Mappings, path_converter,
                     path_join, column_map_diff, ValidateMixin)
from ..params import ClinicalParams
from .DataFile import DataFile


class ColumnMapping(FileBase, ValidateMixin):
    """
    Class with utilities for the column mapping file for clinical data.
    Can be initiated with by giving a clinical params file object.
    """

    # Data label terms that should not be considered variables. These provide metadata
    # for all other column in the row of this data file.
    RESERVED_KEYWORDS = ('SUBJ_ID',
                         'START_DATE',
                         'END_DATE',
                         'MODIFIER',
                         'TRIAL_VISIT_LABEL',
                         'INSTANCE_NUM',
                         'DATA_LABEL',
                         'VISIT_NAME',
                         'SITE_ID',
                         '\\',
                         'OMIT',
                         'PATIENT_VISIT')

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
            setattr(self.params, 'COLUMN_MAP_FILE', os.path.basename(self.path))
        super().__init__()

        self._initial_paths = self.path_id_dict

    @property
    def included_datafiles(self):
        """List of datafiles included in column mapping file."""
        return list(self.df.iloc[:, 0].unique())

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

    def set_concept_path(self, var_id: tuple, path=None, label=None):
        """
        Set the concept path or data label for given variable identifier tuple.

        :param var_id: tuple of filename and column number.
        :param path: new value for path.
        :param label: new value for data label.
        """
        if path is None and label is None:
            raise Exception('Need to give path or label')

        columns_to_update = [self.df.columns[1], self.df.columns[3]]
        new_values = [path, label]
        if path is None:
            columns_to_update.pop(0)
            new_values = new_values[1]
        if label is None:
            columns_to_update.pop(1)
            new_values = new_values[0]

        self.df.loc[tuple(var_id), columns_to_update] = new_values

    def set_reference_column(self, var_id: tuple, value):
        """
        Set the reference column for a variable, this is used for modifiers
        to specify which columns are affected by this modifier variable.

        :param var_id: tuple of filename and column number.
        :param value: value to set reference column to.
        """
        self.df.loc[tuple(var_id), self.df.columns[4]] = value

    def set_concept_code(self, var_id: tuple, value):
        """
        Set the concept code for a variable.

        :param var_id: tuple of filename and column number.
        :param value: value to set concept code to.
        """
        self.df.loc[tuple(var_id), self.df.columns[5]] = value

    def set_column_type(self, var_id: tuple, value: str):
        """
        Set variable to a given data type.

        :param var_id: tuple of filename and column number.
        :param value: value to set column type to.
        """
        self.df.loc[tuple(var_id), self.df.columns[6]] = value

    @staticmethod
    def _df_mods(df):
        """
        _df_mods applies modifications to the dataframe before it is cached.

        :param df: `pd.DataFrame`.
        :return: `pd.DataFrame`.
        """
        df.fillna("", inplace=True)
        df.iloc[:, 2] = df.iloc[:, 2].astype(int)
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
        df.sort_index(inplace=True)
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
                self.msgs.warning("Skipping {!r}, already in column mapping file.".format(var_id))
            except KeyError:
                self.df.loc[i] = [datafile.name, datafile.name, i, name] + cols_min_four

        self.build_index()

    @property
    def subj_id_columns(self):
        """ A list of tuples with datafile and column index for SUBJ_ID, e.g. ('cell-line.txt', 1). """
        response = []
        for datafile in self.included_datafiles:
            subj_id_df = self.df.loc[(self.df.iloc[:, 0] == datafile) & (self.df.iloc[:, 3] == 'SUBJ_ID')]
            for l in subj_id_df.values[:, [0, 2]].tolist():
                response.append((l[0], l[1]))
        return response

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
