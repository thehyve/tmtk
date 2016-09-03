import os
import pandas as pd

from ..utils import FileBase, Exceptions, Mappings, MessageCollector
from ..params import ClinicalParams


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

    def validate(self, verbosity=2):
        messages = MessageCollector(verbosity)

        if self.df.shape[1] != 4:
            messages.error("Wordmapping file does not have 4 columns!")

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
                return dict(zip(rows.ix[:, 2], rows.ix[:, 3]))
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
        df.sortlevel(inplace=True)
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
        df.ix[:, 1] = df.ix[:, 1].astype(int)
        return df
