

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


def get_concept_identifier(variable, study):
    """ Based on a variable concept_code and study, determine the concept identifier. """
    return variable.concept_code or '{}{}{}'.format(study.top_node, Defaults.DELIMITER, variable.concept_path)
