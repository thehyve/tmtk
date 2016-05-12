from .utils import *
from .clinical import *
from .params import Params
from .highdim import *
from .annotation import *
from tmtk.utils.CPrint import CPrint


class Study:
    """
    Describes an entire TranSMART study in ETL.
    """
    def __init__(self, study_params_path=None):
        """
        :param study_params_path:
        """
        if os.path.basename(study_params_path) != 'study.params':
            print('Please give a path to study.params file.')
            raise PathError
        self.params_path = study_params_path
        self.study_folder = os.path.dirname(self.params_path)
        self.Params = Params(self.study_folder)

        # Look for clinical params and create child opbject
        clinical_params = self.find_params_for_datatype(datatypes='clinical')
        if len(clinical_params) == 1:
            self.Clinical = Clinical(clinical_params[0])

        annotation_map = {'microarray_annotation': 'MicroarrayAnnotation',
                          'acgh_annotation': 'ChromosomalRegions',
                          'rnaseq_annotation': 'ChromosomalRegions',
                          'proteomics_annotation': 'ProteomicsAnnotation',
                          'annotation': 'MicroarrayAnnotation',
                          'mrna_annotation': 'MicroarrayAnnotation',
                          }

        annotation_params = self.find_params_for_datatype(datatypes=list(annotation_map))
        if annotation_params:
            self.Annotations = Annotations(annotation_params,
                                           parent=self,
                                           mapping=annotation_map)

        highdim_map = {'rnaseq': 'ReadCounts',
                       'acgh': 'CopyNumberVariation',
                       'expression': 'Expression',
                       'proteomics': 'Proteomics',
                       }

        highdim_params = self.find_params_for_datatype(datatypes=list(highdim_map))
        if highdim_params:
            self.HighDim = HighDim(params_list=highdim_params,
                                   parent=self,
                                   mapping=highdim_map)

    def find_params_for_datatype(self, datatypes=None):
        """
        :param datatypes: single string datatype or list of strings.
        :return: a list of ParamsFile objects for specific datatype in this study.
        """
        if type(datatypes) == 'str':
            datatypes = [datatypes]

        params_list = []
        for key, params_object in self.Params.__dict__.items():
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
            CPrint.warn('Platform {} not found in study.'.format(platform))

        elif len(annotations) == 1:
            return annotations[0]

        else:
            CPrint.error('Duplicate platform objects found for {}: {}').format(platform, annotations)

    def __str__(self):
        statement = "Study object: {}".format(self.params_path)
        return statement

    def validate_all(self, verbosity=2):
        """
        Validate all items in this study.
        :param verbosity: set the verbosity of output, pick 0, 1, or 2.
        :return: True if everything is okay, else return False.
        """
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate_all'):
                obj.validate_all(verbosity=verbosity)

    @property
    def study_id(self):
        study_params = self.find_params_for_datatype('study')[0]
        return study_params.__dict__.get('STUDY_ID')

    def call_boris(self):
        return utils.call_boris(self)
