import pandas as pd

from .. import utils
from ..utils import Mappings


class VariableCollection:
    def __init__(self, clinical_parent=None):
        """
        Collection of Variables. Add datafiles or single variables. Get by variable id_.
        """
        self._variables = {}
        self.parent = clinical_parent

    def add_datafile(self, datafile):
        for i in range(1, datafile.df.shape[1] + 1):  # Column mapping is 1 based
            var = Variable(datafile, i, self.parent)
            self.add_variable(var)

    def add_variable(self, variable):
        self._variables.update({variable.id_: variable})

    def get(self, value):
        return self._variables.get(value)


class Variable:
    """
    Base class for clinical variables
    """
    def __init__(self, datafile, column: int = None, clinical_parent=None):
        self.datafile = datafile
        self.column = column
        self._zero_column = column - 1
        self.parent = clinical_parent

    @property
    def values(self):
        return self.datafile.df.ix[:, self._zero_column]

    @property
    def unique_values(self):
        return self.values.unique()

    @property
    def id_(self):
        return "{}__{}".format(self.datafile.name, self.column)

    @property
    def is_numeric_in_datafile(self):
        return utils.is_numeric(self.unique_values)

    @property
    def is_numeric(self):
        return utils.is_numeric(self.mapped_values) and not self.forced_categorical

    @property
    def is_empty(self):
        return not any([pd.notnull(x) for x in self.unique_values])

    @property
    def concept_path(self):
        """
        Returns concept converted as expected in transmart
        :return:
        """
        cp = self.parent.ColumnMapping.get_concept_path(self.id_)
        return cp.replace('_', ' ').replace('\\', '+').strip('+')

    @property
    def column_map_data(self):
        row = self.parent.ColumnMapping.select_row(self.id_)

        data_args = {}
        for i, s in enumerate(Mappings.column_mapping_header):
            data_args.update({s: row[i] if len(row) > i else None})
        return data_args

    @property
    def word_map_dict(self):
        """
        A dictionary with word mapped variables. Keys are values in the datafile,
        values are what they will be mapped to (through word mapping file)
        :return: dict
        """
        word_map = self.parent.WordMapping.get_word_map(self.id_)
        return {v: word_map.get(v, v) for v in self.unique_values}

    @property
    def mapped_values(self):
        return [v for k, v in self.word_map_dict.items()]

    @property
    def forced_categorical(self):
        return self.column_map_data.get(Mappings.concept_type) == 'CATEGORICAL'

    def validate(self, verbosity=2):
        pass
