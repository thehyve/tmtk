import glob
import os
from .ParamsBase import ParamsBase
from .AnnotationParams import AnnotationParams
from .ClinicalParams import ClinicalParams
from .HighDimParams import HighDimParams
from .TagsParams import TagsParams
from .StudyParams import StudyParams
from .. import utils
from ..utils import CPrint, Mappings


class Params:
    """
    Container class for all params files, called by Study to locate all params files.
    """

    def __init__(self, study_folder=None):
        """
        :param study_folder: points to a study.params file at the root of a study.
        """
        assert os.path.exists(study_folder), 'Params: {} does not exist.'.format(study_folder)

        self._study_folder = study_folder

        for path in glob.iglob(os.path.join(study_folder, '**/*.params'), recursive=True):
            self.add_params(path)

    @staticmethod
    def _pick_subdir_name(relative_path, datatype):
        """
        Private function that finds a suitable subdir name.
        :param relative_path:
        :param datatype:
        :return:
        """
        normalised_path = os.path.normpath(relative_path)
        split_path = normalised_path.strip(os.sep).split(os.sep)
        subdir = '_'.join(split_path[:-1])
        subdir = utils.clean_for_namespace(subdir)
        if not subdir.startswith(datatype):
            subdir = "{}_{}".format(datatype, subdir)
        return subdir

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)

    def add_params(self, path, parameters=None):
        """
        Add a new parameter file to the Params object.
        :param path: a path to a parameter file.
        :param parameters: add dict here with parameters if you want to create a new parameter file.
        """
        datatype = os.path.basename(path).rsplit('.params', 1)[0]
        relative_path = path.split(self._study_folder)[1]
        subdir = self._pick_subdir_name(relative_path, datatype)

        params = self.create_params(path, parameters, subdir=subdir)
        self.__dict__[subdir] = params

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
        params_class = Mappings.params.get(datatype)
        if params_class:
            correct_instance = globals()[params_class]
        elif 'annotation' in datatype:
            correct_instance = globals()['AnnotationParams']
        else:
            CPrint.warn('({}) not supported. skipping.'.format(path))
            return

        return correct_instance(path=path, parameters=parameters, subdir=subdir)
