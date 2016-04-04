class Variable(object):
    """
    Base class for clinical variables
    """
    def __init__(self):
        pass
        self.unique_values = self.get_unique_values()
        # self.concept_path =
        # self.value_type = self.get_value_type()


    def get_unique_values(self):
        pass

    @property
    def value_type(self):
        pass

    @value_type.getter
    def value_type(self):
        pass
