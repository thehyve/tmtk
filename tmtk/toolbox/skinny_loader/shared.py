from ...utils import path_converter

import arrow
import pandas as pd

class TableRow:
    """ Used as base class to create table rows from a pd.Series object defined in child class. """

    def __init__(self):
        self._cached_row = self._row_definition

    @property
    def _row_definition(self):
        """
        Row defined as pd.Series where defaults are be set. Do not change this at runtime.
        This can be retrieved from the initialized object, and then set properties:

            row = self.row
            row.id = 'some_identifier'

        :return: row.
        """
        raise NotImplementedError

    @property
    def row(self):
        """
        Returns a copy of the row defined in self._row_definition

        :return: pd.Series()
        """
        return self._cached_row.copy()

    @property
    def columns(self):
        """
        Columns in this table.
        """
        return self.row.keys()


class Defaults:

    STUDY_NUM = 0
    TRIAL_VISIT = 'General'
    PUBLIC_TOKEN = 'PUBLIC'
    DELIMITER = '\\'


def calc_hlevel(path):
    """ Return the corresponding c_hlevel for a given path. """
    return len(path.strip(Defaults.DELIMITER).split(Defaults.DELIMITER)) - 1


def get_full_path(variable, study):
    """ Concatenates study top_node and variable concept path """
    path = '{}\\{}'.format(study.top_node, variable.concept_path)
    return path_slash_all(path_converter(path))


def path_slash_all(path):
    if not path.startswith('\\'):
        path = '\\' + path
    if not path.endswith('\\'):
        path += '\\'
    return path


def get_unix_timestamp(date):
    """ Returns timestamp if date is not None or pd.np.nan, else returns nan """
    if date not in (None, pd.np.nan):
        try:
            return arrow.get(date).format('X') + '000'  # transmart needs milliseconds
        except OSError:
            return pd.np.nan
    else:
        return pd.np.nan
