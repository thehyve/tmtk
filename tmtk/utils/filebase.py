import os
import pandas as pd

from . import cached_property, file2df, df2file, CPrint


class FileBase:
    """
    Super class with shared utilities for file objects.
    """

    def __init__(self):
        self._hash_init = None

    # The df property is setup like this so dataframe are only loaded from disk on first request.
    # Upon load self._df_mods will be performed if this method has been defined.  After first
    # reading from disk, the results are cached and df will just return the pd.DataFrame.
    @cached_property
    def _df(self):
        if self.path and os.path.exists(self.path) and self.tabs_in_first_line():
            df = file2df(self.path)
        else:
            CPrint.warn("No valid file found on disk for {}, creating dataframe.".format(self))
            df = self.create_df()
        df = self._df_processing(df)
        self._hash_init = hash(df.__bytes__())
        return df

    @property
    def df(self):
        """The pd.DataFrame for this file object."""
        return self._df

    @df.setter
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise TypeError('Expected pd.DataFrame object.')
        value = self._df_processing(value)
        self._hash_init = self._hash_init or 1
        self._df = value

    def _df_processing(self, df):
        """
        Gives df post load modifications

        :param df: the `pd.DataFrame`
        :return: modified dataframe
        """
        try:
            df = self._df_mods(df)
        except AttributeError:
            pass
        try:
            df = self.build_index(df)
        except AttributeError:
            pass
        return df

    def __hash__(self):
        return hash(self.df.__bytes__())

    @property
    def df_has_changed(self):
        return not hash(self) == self._hash_init

    @property
    def header(self):
        return self.df.columns

    @property
    def name(self):
        return os.path.basename(self.path)

    @name.setter
    def name(self, value):
        self.path = os.path.join(os.path.dirname(self.path), value)

    def __repr__(self):
        return self.path

    def tabs_in_first_line(self):
        """Check if file is tab delimited."""
        with open(self.path, 'r') as file:
            has_tab = '\t' in file.readline()

        if has_tab:
            return True
        CPrint.warn('{} is invalid as it contains no tabs on first line.'.format(self))

    def write_to(self, path, overwrite=False):
        """
        Wrapper for :func:`tmtk.utils.df2file()`.

        :param path: path to write file to.
        :param overwrite: write over existing files in the filesystem)
        """
        df2file(self.df, path, overwrite=overwrite)

    def save(self):
        """Overwrite the original file with the current dataframe."""
        self.write_to(self.path, overwrite=True)
