import os

import pandas as pd

from ..params import ClinicalParams
from ..utils import FileBase, Exceptions, Mappings, MessageCollector, word_map_diff


class WordMapping(FileBase):
    """
    Class representing the word mapping file.
    """

    def __init__(self, params=None):
        """
        Initialize by giving a params object.

        :param params: `tmtk.ClinicalParams`.
        """

        self.params = params

        if not isinstance(params, ClinicalParams):
            raise Exceptions.ClassError(type(params))
        elif params.get('WORD_MAP_FILE'):
            self.path = os.path.join(params.dirname, params.WORD_MAP_FILE)
        else:
            self.path = os.path.join(params.dirname, 'word_mapping_file.txt')
            self.params.__dict__['WORD_MAP_FILE'] = os.path.basename(self.path)

        super().__init__()
        self._initial_word_map = self.word_map_dicts

    def validate(self, verbosity=2):

        messages = MessageCollector(verbosity)

        if self.df.shape[1] != 4:
            messages.error("Wordmapping file does not have 4 columns!")

        # check presence of all data files
        filenames = self.df.iloc[:, 0].unique()
        valid_filenames = []
        for filename in filenames:
            if filename not in os.listdir(self.params.dirname):
                msg = "The file {} doesn't exists".format(filename)
                messages.error(msg)
            else:
                absolute_filename = os.path.join(self.params.dirname, filename)
                valid_filenames.append(absolute_filename)

        dfs = {os.path.basename(filename): pd.read_table(filename) for filename in valid_filenames}
        for filename, df in dfs.items():
            column_number = df.shape[1]

            rows = [row for index, row in self.df.iterrows() if row[0] == filename]
            columns = {row[1] for row in rows}

            out_of_bound = {index for index in columns if index > column_number}
            for index in out_of_bound:
                msg = "File {} doesn't has {} columns, but {} columns".format(filename, index, column_number)
                messages.error(msg)

            correct_columns = columns - out_of_bound
            for column in correct_columns:
                mapped_values = {row[2] for row in rows if row[1] == column}
                index = column - 1
                data_values = set(df.iloc[:, index].unique())

                unmapped = mapped_values - data_values
                for unmapped_value in unmapped:
                    msg = "Value {} is mapped at column {} in file {}. " \
                          "However the value is not present in the column".format(unmapped_value, column, filename)
                    messages.warn(msg)

        messages.flush()
        return not messages.found_error

    def get_word_map(self, var_id):
        """
        Return dict with value in data file, and the mapped value
        as keyword-value pairs.

        :param var_id: tuple of filename and column number.
        :return: dict.
        """
        var_id = tuple(var_id)

        if var_id in self.df.index:
            rows = self.df.loc[var_id]
            if isinstance(rows, pd.DataFrame):
                return dict(zip(rows.iloc[:, 2], rows.iloc[:, 3]))
            else:
                return {rows[2]: rows[3]}

        else:
            return {}

    def build_index(self, df=None):
        """
        Build and sort multi-index for dataframe based on filename and
        column number columns. If no df parameter is not set, build index
        for self.df.

        :param df: `pd.DataFrame`.
        :return: `pd.DataFrame`.
        """
        if not isinstance(df, pd.DataFrame):
            df = self.df
        df.set_index(list(df.columns[[0, 1]]), drop=False, inplace=True)
        df.sort_index(inplace=True)
        return df

    def create_df(self):
        """
        Create `pd.DataFrame` with a correct header.

        :return: `pd.DataFrame`.
        """
        df = pd.DataFrame(dtype=str, columns=Mappings.word_mapping_header)
        df = self.build_index(df)
        return df

    @staticmethod
    def _df_mods(df):
        """
        _df_mods applies modifications to the dataframe before it is cached.

        :param df: `pd.DataFrame`.
        :return: `pd.DataFrame`.
        """
        df.iloc[:, 1] = df.iloc[:, 1].astype(int)
        return df

    @property
    def word_map_dicts(self):
        """Dictionary with all variable ids as keys and word map dicts as value."""
        return {t: self.get_word_map(t) for t in self.df.index}

    def word_map_changes(self, silent=False):
        """
        Determine changes made to word mapping file.

        :param silent: if True, only print output.
        :return: if `silent=False` return dictionary with changes since load.
        """
        diff = word_map_diff(self._initial_word_map, self.word_map_dicts)
        if not silent:
            for var_id, d in diff.items():
                print("{}: {}".format(*var_id))
                for k, v in d.items():
                    print("        {!r} -> {!r}".format(k, v))
        else:
            return diff
