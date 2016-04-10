import tmtk.utils as utils


class Variable:
    """
    Base class for clinical variables
    """
    def __init__(self):
        pass
        self.unique_values = self.get_unique_values()
        # self.concept_path =
        self.is_categorical = self.get_value_type()

    def get_unique_values(self):
        pass

    def get_value_type(self):
        """
        Return True if transmart would consider this to be of categorical datatype.
        """
        values = self.unique_values
        return utils.is_categorical(values)

