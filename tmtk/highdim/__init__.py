from .HighDimBase import HighDimBase
from .CopyNumberVariation import CopyNumberVariation
from .Expression import Expression
from .Proteomics import Proteomics
from .ReadCounts import ReadCounts
from .Mirna import Mirna
from .SampleMapping import SampleMapping
import tmtk.utils as utils
from tmtk.utils.CPrint import CPrint


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
            try:
                self.__dict__[str(p)] = new_instance(p, parent=parent)
            except utils.PathError:
                continue

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)

    def update_high_dim_paths(self, high_dim_paths):
        """

        :param high_dim_paths:
        :return:
        """
        changed_dict = {k: path for k, path in high_dim_paths.items() if utils.md5(path) != k}
        if changed_dict:
            CPrint.okay('Found ({}) changed concept paths.'.format(len(changed_dict)))
        else:
            CPrint.info('No changes found in any HighDim paths.')
            return

        for ss in self.subject_sample_mappings:
            ss.update_concept_paths(changed_dict)

    @property
    def subject_sample_mappings(self):
        return [x.sample_mapping for k, x in self.__dict__.items() if hasattr(x, 'sample_mapping')]
