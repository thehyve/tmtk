from .ParamsBase import ParamsBase
from .AnnotationParams import AnnotationParams
from .ClinicalParams import ClinicalParams
from .HighDimParams import HighDimParams
from .TagsParams import TagsParams
from .StudyParams import StudyParams
import glob
import os
from .. import utils
import tmtk.utils.CPrint as CPrint


class Params:
    """
    Container class for all params files, called by Study to locate all params files.
    """
    def __init__(self, study_folder=None):
        """
        :param study_folder: points to a study.params file at the root of a study.
        """
        assert os.path.exists(study_folder), 'Params: {} does not exist.'.format(study_folder)

        param_mapping = {'rnaseq': 'HighDimParams',
                         'cnv': 'HighDimParams',
                         'proteomics': 'HighDimParams',
                         'expression': 'HighDimParams',
                         'tags': 'TagsParams',
                         'study': 'StudyParams',
                         'clinical': 'ClinicalParams',
                         'mirna': 'HighDimParams'
                         }

        for f in glob.iglob(os.path.join(study_folder, '**/*.params'), recursive=True):
            datatype = os.path.basename(f).split('.params')[0]
            if 'kettle' in str(f):  # Skip subdirectories that have kettle in the name.
                CPrint.warn('Skipping ({}) because of "kettle"'.format(f))
                continue

            params_class = param_mapping.get(datatype, None)
            if params_class:
                correct_instance = globals()[params_class]
            elif 'annotation' in datatype:
                correct_instance = globals()['AnnotationParams']
            else:
                CPrint.warn('({}) not supported. skipping.'.format(f))
                continue

            relative_path = f.split(study_folder)[1]
            subdir = self._pick_subdir_name(relative_path, datatype)
            self.__dict__[subdir] = correct_instance(path=f, datatype=datatype, subdir=subdir)

    @staticmethod
    def _pick_subdir_name(relative_path, datatype):
        """
        Private function that finds a suitable subdir name.
        :param relative_path:
        :param datatype:
        :return:
        """
        split_path = relative_path.strip('/').split('/')
        subdir = '_'.join(split_path[:-1])
        subdir = utils.clean_for_namespace(subdir)
        if not subdir.startswith(datatype):
            subdir = "{}_{}".format(datatype, subdir)
        return subdir

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)
