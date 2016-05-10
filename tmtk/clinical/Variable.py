import tmtk.utils as utils


class Variable:
    """
    Base class for clinical variables
    """
    def __init__(self, datafile, column: int = None):
        self.df = datafile.df
        self.datafile = datafile
        self.column = column
        # self.concept_path =

    @property
    def values(self):
        return self.df.ix[:, self.column]

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
