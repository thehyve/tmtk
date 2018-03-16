from ..utils import path_converter, md5, Mappings, PathError, FileBase, ValidateMixin


class HighDim(ValidateMixin):
    """
    Container class for all High Dimensional data types.

    :param params_list: contains a list with Params objects.
    """

    def __init__(self, params_list=None, parent=None):
        assert type(params_list) == list, \
            'Expected list with annotation params, but got {}.'.format(type(params_list))

        for p in params_list:
            new_instance = Mappings.get_highdim(p.datatype)
            try:
                self.__dict__[p.subdir] = new_instance(p, parent=parent)
            except PathError:
                continue

    def validate_all(self, verbosity='INFO'):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)

    def update_high_dim_paths(self, high_dim_paths):
        """
        Update sample mapping if path has been changed.

        :param high_dim_paths: dictionary with paths and old concept paths.
        """
        changed_dict = {k: path for k, path in high_dim_paths.items() if md5(path_converter(path)) != k}
        if changed_dict:
            self.msgs.okay('Found ({}) changed concept paths.'.format(len(changed_dict)))
        else:
            self.msgs.info('No changes found in any HighDim paths.')
            return

        for ss in self.sample_mapping_files:
            ss.update_concept_paths(changed_dict)

    @property
    def high_dim_files(self):
        return [x for k, x in self.__dict__.items() if issubclass(type(x), FileBase)]

    @property
    def sample_mapping_files(self):
        return [x.sample_mapping for x in self.high_dim_files]
