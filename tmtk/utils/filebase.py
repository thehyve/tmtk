from tmtk.utils import cached_property, file2df, CPrint
import os


class FileBase:
    """
    Super class with shared utilities for file objects.
    """
    def __init__(self):
        self._hash_init = None

    @cached_property
    def df(self):
        if self.path and os.path.exists(self.path) and self.tabs_in_first_line():
            df, self._hash_init = file2df(self.path, hashed=True)
        else:
            CPrint.warn("No valid file found on disk for {}, creating dataframe.".format(self))
            df = self.create_df()
        return df

    @property
    def _hash(self):
        return hash(self.df.__bytes__())

    @property
    def df_has_changed(self):
        return not self._hash == self._hash_init

    @property
    def header(self):
        return self.df.columns

    def __repr__(self):
        return self.path

    def tabs_in_first_line(self):
        with open(self.path, 'r') as file:
            has_tab = '\t' in file.readline()

        if has_tab:
            return True
        CPrint.warn('{} is invalid as it contains no tabs on first line.'.format(self))
