import os

from pathlib import Path

from ..utils import Mappings, clean_for_namespace, ValidateMixin, Message


class Params(ValidateMixin):
    """
    Container class for all params files, called by Study to locate all params files.
    """

    def __init__(self, study_folder=None):
        """
        Initialize by giving a path to study.params file at the root of a study.

        :param study_folder: path
        """
        assert os.path.exists(study_folder), 'Params: {} does not exist.'.format(study_folder)

        self._study_folder = study_folder

        for path in Path(study_folder).glob('**/*.params'):
            self.add_params(str(path))

    @staticmethod
    def _pick_subdir_name(relative_path, datatype):
        """
        Return a sensible subdirectory name, which is safe for namespace.

        :param relative_path: path of directory with data files
        :param datatype: datatype that will be prepended
        :return: subdir string.
        """
        normalised_path = os.path.normpath(relative_path)
        split_path = normalised_path.strip(os.sep).split(os.sep)
        subdir = '_'.join(split_path[:-1])
        subdir = clean_for_namespace(subdir)
        if not subdir.startswith(datatype):
            subdir = "{}_{}".format(datatype, subdir)
        return subdir.strip('_')

    def add_params(self, path, parameters=None):
        """
        Add a new parameter file to the Params object.

        :param path: a path to a parameter file.
        :param new: if new, create parameter object.
        :param parameters: add dict here with parameters if you want to create a new parameter file.
        """
        datatype = os.path.basename(path).rsplit('.params', 1)[0]
        relative_path = path.split(self._study_folder)[1]
        subdir = self._pick_subdir_name(relative_path, datatype)

        params = self.create_params(path, parameters, subdir=subdir)

        if params:
            self.__dict__[subdir] = params

        return params

    @staticmethod
    def create_params(path, parameters=None, subdir=None):
        """
        Create a new parameter file object.

        :param path: a path to a parameter file.
        :param parameters: add dict here with parameters if you want to create a new parameter file.
        :param subdir: subdir is used as string representation.
        :return: parameter file object.
        """
        datatype = os.path.basename(path).split('.params')[0]

        try:
            params_class = Mappings.get_params(datatype)
        except KeyError:
            Message.warning('({}) not supported. skipping.'.format(path))
        else:
            return params_class(path=path, parameters=parameters, subdir=subdir)
