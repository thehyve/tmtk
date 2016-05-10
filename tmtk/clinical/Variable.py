import tmtk.utils as utils


class VariableCollection:
    def __init__(self):
        """
        Collection of Variables. Add datafiles or single variables. Get by variable id_.
        """
        self._variables = {}

    def add_datafile(self, datafile):
        for i in range(1, datafile.df.shape[1] + 1):  # Column mapping is 1 based
            var = Variable(datafile, i)
            self.add_variable(var)

    def add_variable(self, variable):
        self._variables.update({variable.id_: variable})

    def get(self, value):
        return self._variables.get(value)


class Variable:
    """
    Base class for clinical variables
    """
    def __init__(self, datafile, column: int = None):
        self.df = datafile.df
        self.datafile = datafile
        self.column = column
        self._zero_column = column - 1

    @property
    def values(self):
        return self.df.ix[:, self._zero_column]

    @property
    def unique_values(self):
        return self.values.unique()

    @property
    def id_(self):
        return "{}__{}".format(self.datafile.name, self.column)

    @property
    def is_numeric(self):
        return utils.is_numeric(self.unique_values)

    def validate(self, verbosity=2):
        pass
