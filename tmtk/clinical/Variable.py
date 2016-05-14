import tmtk.utils as utils


FILENAME = 'Filename'
CATEGORY_CODE = 'Category Code'
COLUMN_NUMBER = 'Column Number'
DATA_LABEL = 'Data Label'
MAGIC_5 = 'Data Label Source'
MAGIC_6 = 'Control Vocab Cd'


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
        return utils.is_numeric(self.mapped_values)

    @property
    def concept_path(self):
        return self.parent.ColumnMapping.get_concept_path(self.id_)

    @property
    def column_map_data(self):
        row = self.parent.ColumnMapping.select_row(self.id_)
        data_args = {FILENAME: row[0],
                     CATEGORY_CODE: row[1],
                     COLUMN_NUMBER: row[2],
                     DATA_LABEL: row[3],
                     MAGIC_5: row[4] if len(row) > 4 else None,
                     MAGIC_6: row[5] if len(row) > 5 else None,
                     }
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

    def validate(self, verbosity=2):
        pass
