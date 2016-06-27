import os
import json
from .clinical import Clinical
from .params import Params
from .highdim import HighDim
from .annotation import Annotations
from .tags import MetaDataTags
from .utils import CPrint
from tmtk import utils, arborist


class Study:
    """
    Describes an entire TranSMART study in ETL.
    """
    def __init__(self, study_params_path=None, minimal=False):
        """
        :param study_params_path:
        """
        if os.path.basename(study_params_path) != 'study.params':
            print('Please give a path to study.params file.')
            raise utils.PathError
        self.params_path = os.path.abspath(study_params_path)
        self.study_folder = os.path.dirname(self.params_path)
        self.Params = Params(self.study_folder)

        if minimal:
            return

        # Look for clinical params and create child object
        clinical_params = self.find_params_for_datatype(datatypes='clinical')
        if len(clinical_params) == 1:
            self.Clinical = Clinical(clinical_params[0])

        annotation_map = {'microarray_annotation': 'MicroarrayAnnotation',
                          'cnv_annotation': 'ChromosomalRegions',
                          'rnaseq_annotation': 'ChromosomalRegions',
                          'proteomics_annotation': 'ProteomicsAnnotation',
                          'annotation': 'MicroarrayAnnotation',
                          'mrna_annotation': 'MicroarrayAnnotation',
                          'mirna_annotation': 'MirnaAnnotation',
                          }

        annotation_params = self.find_params_for_datatype(datatypes=list(annotation_map))
        if annotation_params:
            self.Annotations = Annotations(annotation_params,
                                           parent=self,
                                           mapping=annotation_map)

        highdim_map = {'rnaseq': 'ReadCounts',
                       'cnv': 'CopyNumberVariation',
                       'expression': 'Expression',
                       'proteomics': 'Proteomics',
                       'mirna': 'Mirna',
                       }

        highdim_params = self.find_params_for_datatype(datatypes=list(highdim_map))
        if highdim_params:
            self.HighDim = HighDim(params_list=highdim_params,
                                   parent=self,
                                   mapping=highdim_map)

        tags_params = self.find_params_for_datatype(datatypes='tags')
        if tags_params:
            self.Tags = MetaDataTags(params=tags_params[0],
                                     parent=self)

    def find_params_for_datatype(self, datatypes=None):
        """
        :param datatypes: single string datatype or list of strings.
        :return: a list of ParamsFile objects for specific datatype in this study.
        """
        if type(datatypes) == 'str':
            datatypes = [datatypes]

        params_list = []
        for key, params_object in self.Params.__dict__.items():
            try:
                if params_object.datatype in datatypes:
                    params_list.append(params_object)
            except AttributeError:
                pass

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
        :param verbosity: set the verbosity of output, pick 0, 1, or 2, 3 or 4.
        :return: True if everything is okay, else return False.
        """
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate_all'):
                obj.validate_all(verbosity=verbosity)

    def files_with_changes(self):
        """
        Find dataframes that have changed since they have been loaded
        """
        changed = []

        for obj in self.get_objects_with_prop('df_has_changed'):
            if obj.df_has_changed:
                CPrint.warn('({}) Dataframe has changed.'.format(obj))
                changed.append(obj)
            else:
                CPrint.info('({}) has not changed.'.format(obj))
        return changed

    def get_objects_with_prop(self, prop: all):
        """
        Search for objects with a certain property.
        :param prop: string equal to the property name.
        :return:
        """
        for key, obj in self.__dict__.items():
            if hasattr(obj, prop):
                yield obj

            if not hasattr(obj, '__dict__'):
                continue

            for k, o in obj.__dict__.items():
                if hasattr(o, 'sample_mapping'):
                    if hasattr(o.sample_mapping, prop):
                        yield o.sample_mapping

                if hasattr(o, prop):
                    yield o

    @property
    def study_id(self):
        study_params = self.find_params_for_datatype('study')[0]
        return study_params.__dict__.get('STUDY_ID')

    def call_boris(self):
        arborist.call_boris(self)

    @property
    def subject_sample_mappings(self):
        return self.HighDim.subject_sample_mappings if hasattr(self, 'HighDim') else []

    @property
    def concept_tree(self):
        return arborist.create_tree_from_study(self)

    def update_from_treefile(self, treefile):
        """
        Give path to a treefile (from Boris as a Service or otherwise) and update the current
        study to match made changes.
        :param treefile:
        :return:
        """
        with open(treefile, 'r') as f:
            json_data = json.loads(f.read())
            arborist.update_study_from_json(self, json_data)

    def add_metadata(self):
        if hasattr(self, 'Tags'):
            CPrint.okay("Study metadata tags found.")
            return

        params_path = os.path.join(self.study_folder, 'tags', 'tags.params')
        self.Params.add_params(params_path, parameters={'TAGS_FILE': 'tags.txt'})
        tag_param = self.find_params_for_datatype('tags')[0]
        self.Tags = MetaDataTags(params=tag_param, parent=self)

    def save_to(self, root_dir, overwrite=False):
        """
        Write this study to a new directory on file system.
        :param root_dir: a
        :param overwrite: set this to True to overwrite existing files.
        :return:
        """
        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            os.makedirs(root_dir)

        for obj in self.get_objects_with_prop('path'):
            # Strip sub_path from leading slash, as os.path.join() will think its an absolute path
            sub_path = obj.path.split(self.study_folder)[1].strip('/')
            new_path = os.path.join(root_dir, sub_path)
            CPrint.info("Writing file to {}".format(new_path))
            obj.write_to(new_path, overwrite=overwrite)

