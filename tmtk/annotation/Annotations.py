import tmtk.utils as utils


class Annotations:
    """
    Class containing all AnnotationFile objects.
    """

    def __init__(self, params_list=None, parent=None):
        """

        :param params_list: contains a list with Params objects.
        :param parent:
        """
        assert type(params_list) == list, \
            'Expected list with annotation params, but got {}.'.format(type(params_list))

        for p in params_list:

            new_instance = utils.Mappings.get_annotations(p.datatype)

            try:
                af = new_instance(p)
            except utils.PathError:
                continue

            annotation_type = p.datatype.split('annotation')[0]

            platform_key = annotation_type + af.platform
            platform_key = utils.clean_for_namespace(platform_key)
            self.__dict__[platform_key] = af

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)
