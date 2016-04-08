from .SampleMapping import SampleMapping
from .ReadCounts import ReadCounts
from .Annotations import AnnotationFile, Annotations
from .Base import HighDimBase
from .CopyNumberVariantion import CopyNumberVariation
from .Expression import Expression


class HighDim(object):
    """
    Container class for all High Dimensional data types.
    """
    def __init__(self, params_list=None, parent=None):
            for p in params_list:
                if p.datatype == 'rnaseq':
                    self.__dict__[str(p)] = ReadCounts(p, parent=parent)
                if p.datatype == 'acgh':
                    self.__dict__[str(p)] = CopyNumberVariation(p, parent=parent)
                if p.datatype == 'expression':
                    self.__dict__[str(p)] = Expression(p, parent=parent)
