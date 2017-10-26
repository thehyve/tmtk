import os

import pandas as pd

from ..utils import FileBase, Exceptions, Mappings, word_map_diff, ValidateMixin
from ..params import ClinicalParams


class WordMapping(FileBase, ValidateMixin):
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

    def _validate_dimensions(self):
        if self.df.shape[1] != 4:
            self.msgs.error("Wordmapping file does not have 4 columns!")

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

    def set_word_map(self, var_id, d):
        """
        Set the word mapping for specific variable based on its filename and column number.

        :param var_id: variable identifier tuple.
        :param d: dictionary that contains the value map.
        """
        var_id = tuple(var_id)

        self.df.drop(var_id, inplace=True, errors='ignore')

        self.df = self.df.append(
                        pd.DataFrame(
                            [[var_id[0], var_id[1], k, v] for k, v in d.items()],
                            columns=self.df.columns
                        ),
                        ignore_index=True)

    @property
    def included_datafiles(self):
        """List of datafiles included in word mapping file."""
        return list(self.df.iloc[:, 0].unique())
    
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
