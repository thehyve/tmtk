from .AnnotationBase import AnnotationBase
from .ChromosomalRegions import ChromosomalRegions
from .MicroarrayAnnotation import MicroarrayAnnotation
from .ProteomicsAnnotation import ProteomicsAnnotation
from .MirnaAnnotation import MirnaAnnotation
import tmtk.utils as utils


class Annotations:
    """
    Class containing all AnnotationFile objects.
    """
    def __init__(self, params_list=None, parent=None, mapping=None):
        """
        :param params_list: contains a list with Params objects.
        :param parent:
        :param mapping: dictionary that that points params to the right Subclass.
        e.g. {'rnaseq': 'ReadCountsAnnotation'}.
        """
        assert type(params_list) == list, \
            'Expected list with annotation params, but got {}.'.format(type(params_list))
        assert type(mapping) == dict, \
            'Expected dict with annotation params identifiers and corresponding class names, ' \
            'but got {}.'.format(type(mapping))

        for p in params_list:

            new_instance = globals()[mapping[p.datatype]]

            try:
                af = new_instance(p)
            except utils.PathError:
                continue

            annotation_type = p.datatype.split('annotation')[0]
            # Useful because microarrays annotation params have not been renamed yet.
            if not annotation_type:
                annotation_type = 'microarray_'

            platform_key = annotation_type + af.platform
            platform_key = utils.clean_for_namespace(platform_key)
            self.__dict__[platform_key] = af

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)