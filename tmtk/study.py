import glob
from .utils import *
from .clinical import *
from .params import ParamsFile
from .highdim import *


class Study(object):
    """
    Describes an entire TranSMART study in ETL.

    :param study_params_path: points to a study.params file at the root of a study.
    """
    def __init__(self, study_params_path=None):
        if os.path.basename(study_params_path) != 'study.params':
            print('Please give a path to study.params file.')
            raise PathError
        self.params_path = study_params_path
        self.study_folder = os.path.dirname(self.params_path)
        self.Params = Bunch(self._create_params_list())

        clinical_params = self.find_params_for_datatype(datatypes='clinical')
        if len(clinical_params) == 1:
            self.Clinical = Clinical(clinical_params[0])

        annotation_types = ['microarray_annotation',
                            'acgh_annotation',
                            'rnaseq_annotation',
                            'annotation',
                            ]
        annotation_params = self.find_params_for_datatype(datatypes=annotation_types)
        if annotation_params:
            self.Annotations = Annotations(annotation_params)

        highdim_types = ['rnaseq',
                         'acgh',
                         'expression'
                         ]

        highdim_params = self.find_params_for_datatype(datatypes=highdim_types)
        if highdim_params:
            self.HighDim = HighDim(params_list=highdim_params, parent=self)

    def _create_params_list(self):
        """
        Private function finds all parameter files in study subdirectories.
        """
        params = {}
        for f in glob.iglob(os.path.join(self.study_folder, '*/**/*.params'), recursive=True):
            datatype = os.path.basename(f).split('.params')[0]
            if 'kettle' in str(f):
                continue
            subdir = self._pick_subdir_name(f, datatype)
            params[subdir] = ParamsFile(path=f, datatype=datatype, subdir=subdir)
        return params

    def _pick_subdir_name(self, abs_path, datatype):
        """
        Private function that finds a suitable subdir name.
        """
        relative_dir = abs_path.split(self.study_folder)[1]
        split_path = relative_dir.strip('/').split('/')
        subdir = '_'.join(split_path[:-1])
        subdir = Bunch.clean_for_namespace(subdir)
        if not subdir.startswith(datatype):
            subdir = "{}_{}".format(datatype, subdir)
        return subdir

    def find_params_for_datatype(self, datatypes=None):
        """
        :param datatypes: single string datatype or list of strings.
        :return: a list of ParamsFile objects for specific datatype in this study.
        """
        if type(datatypes) == 'str':
            datatypes = [datatypes]

        params_list = []
        for key, params_object in self.Params.as_dict.items():
            if params_object.datatype in datatypes:
                params_list.append(params_object)
        return params_list

    def find_annotation(self, platform=None):
        """
        :param platform: platform id to look for in this study.
        :return: a AnnotationFile object.
        """
        annotations = []
        for key, params_object in self.Annotations.__dict__.items():
            if params_object.platform == platform:
                annotations.append(params_object)

        if not annotations:
            print('Platform {} not found in study.'.format(platform))

        elif len(annotations) == 1:
            return annotations[0]

        else:
            print('Duplicate platform objects found for {}: {}').format(platform, annotations)

    def __str__(self):
        statement = "Study object: {}".format(self.params_path)
        return statement

    def validate_all(self):
        for key, params_object in self.Params.as_dict.items():
            params_object.validate()

