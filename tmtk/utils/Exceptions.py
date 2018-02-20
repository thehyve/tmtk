class ClassError(Exception):
    """
    Error raised when unexpected class is found.

    :param found: is the Object class of found
    :param expected: is the required Object class
    """

    def __init__(self, found=None, expected=None):
        self.found = found
        self.expected = expected

    def __str__(self):
        return "Got {} where {} was expected.".format(self.found, self.expected)


class DatatypeError(Exception):
    """
    Error raised when incorrect datatype is found.

    :param found: is the datatype of object
    :param expected: is the required datatype
    """

    def __init__(self, found=None, expected=None):
        self.found = found
        self.expected = expected

    def __str__(self):
        return "Got {} where {} was expected.".format(self.found, self.expected)


class PathError(Exception):
    """Error raised when an incorrect path is given."""

    def __init__(self, found=None):
        self.found = found

    def __str__(self):
        return "{}.".format(self.found)


class TooManyValues(Exception):
    """Error raised when too many values are found."""

    def __init__(self, found=None, expected=None, id_=None):
        self.found = found
        self.expected = expected
        self.id_ = id_

    def __str__(self):
        return "Found {} values for {}, expected {}.".format(self.found, self.expected, self.id_)


class ReservedKeywordException(Exception):
    pass


class BlueprintException(Exception):
    pass


class ArboristException(Exception):
    pass
