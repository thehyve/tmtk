from .HighDimBase import HighDimBase
from .CopyNumberVariation import CopyNumberVariation
from .Expression import Expression
from .Proteomics import Proteomics
from .ReadCounts import ReadCounts
from .SampleMapping import SampleMapping


class HighDim:
    """
    Container class for all High Dimensional data types.
    :param params_list: contains a list with Params objects.
    :param mapping: dictionary that that points params to the right Subclass.
    e.g. {'rnaseq': 'ReadCounts'}.
    """
    def __init__(self, params_list=None, parent=None, mapping=None):
        assert type(params_list) == list, \
            'Expected list with annotation params, but got {}.'.format(type(params_list))
        assert type(mapping) == dict, \
            'Expected dict with annotation params identifiers and corresponding class names, ' \
            'but got {}.'.format(type(mapping))

        for p in params_list:
            new_instance = globals()[mapping[p.datatype]]
            self.__dict__[str(p)] = new_instance(p, parent=parent)
