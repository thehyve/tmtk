from .ParamsBase import ParamsBase
from .AnnotationParams import AnnotationParams
from .ClinicalParams import ClinicalParams
from .HighDimParams import HighDimParams
from .TagsParams import TagsParams
import glob
import os
import tmtk.utils as utils


class Params:
    """
    Container class for all params files, called by Study to locate all params files.
    """
    def __init__(self, study_folder=None):
        """
        :param study_folder: points to a study.params file at the root of a study.
        """
        assert os.path.exists(study_folder), 'Params: {} does not exist.'.format(study_folder)

        for f in glob.iglob(os.path.join(study_folder, '*/**/*.params'), recursive=True):
            datatype = os.path.basename(f).split('.params')[0]
            if 'kettle' in str(f):  # Skip subdirectories that have kettle in the name.
                continue

            if datatype in ['rnaseq', 'acgh', 'proteomics', 'expression']:
                correct_instance = globals()['HighDimParams']
            elif 'annotation' in datatype:
                correct_instance = globals()['AnnotationParams']
            elif datatype == 'clinical':
                correct_instance = globals()['ClinicalParams']
            elif datatype == 'tags':
                correct_instance = globals()['TagsParams']
            else:
                raise Exception

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
