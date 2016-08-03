import os

from tmtk.utils import cached_property, file2df, df2file, CPrint


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
            # Give a class a _df_mods method to make specific modifications before load
            if hasattr(self, '_df_mods'):
                df = self._df_mods(df)
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

    @property
    def name(self):
        return os.path.basename(self.path)

    @name.setter
    def name(self, value):
        self.path = os.path.join(os.path.dirname(self.path), value)

    def __repr__(self):
        return self.path

    def tabs_in_first_line(self):
        with open(self.path, 'r') as file:
            has_tab = '\t' in file.readline()

        if has_tab:
            return True
        CPrint.warn('{} is invalid as it contains no tabs on first line.'.format(self))

    def write_to(self, path, overwrite=False):
        """
        Wrapper for tmtk.utils.df2file().
        :param path: path to write file to.
        :param overwrite: write over existing files in the filesystem)
        """
        df2file(self.df, path, overwrite=overwrite)

    def save(self):
        """
        Overwrite the original file with the current dataframe.
        """
        self.write_to(self.path, overwrite=True)
