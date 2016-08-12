import os
import json
from IPython.display import HTML

from .clinical import Clinical
from .params import Params
from .highdim import HighDim
from .annotation import Annotations
from .tags import MetaDataTags
from .utils import CPrint, Mappings
from tmtk import utils, arborist


class Study:
    """
    Describes an entire TranSMART study.  This is the main object used
    in tmtk. Studies can be initialized by pointing to a study.params file.
    This study has to be structured according to specification for
    transmart-batch.

    >>> import tmtk
    >>> study = tmtk.Study('./studies/valid_study/study.params')

    This will create the study object which can be used as a starting point
    for custom curation or directly in The Arborist.

    """

    def __init__(self, study_params_path=None, minimal=False):
        """
        Studies can be initialized by pointing to a study.params file.

        :param study_params_path: valid path to a study.params.
        :param minimal: if True, tmtk will only load parameter files.
        """
        if os.path.basename(study_params_path) != 'study.params':
            print('Please give a path to study.params file.')
            raise utils.PathError
        self.params_path = os.path.abspath(study_params_path)
        self.study_folder = os.path.dirname(self.params_path)
        self.Params = Params(self.study_folder)

        if minimal:
            return

        self.Clinical = None
        # Look for clinical params and create child object
        clinical_params = self.find_params_for_datatype(datatypes='clinical')
        if clinical_params:
            self.add_clinical(clinical_params[0])

        annotation_params = self.find_params_for_datatype(list(Mappings.get_annotations()))
        if annotation_params:
            self.Annotations = Annotations(annotation_params,
                                           parent=self)

        highdim_params = self.find_params_for_datatype(list(Mappings.get_highdim()))
        if highdim_params:
            self.HighDim = HighDim(params_list=highdim_params,
                                   parent=self)

        tags_params = self.find_params_for_datatype(datatypes='tags')
        if tags_params:
            self.Tags = MetaDataTags(params=tags_params[0],
                                     parent=self)

    def find_params_for_datatype(self, datatypes=None):
        """
        Search for parameter files within this study object and return them as list.

        :param datatypes: single string datatype or list of strings
        :return: a list of parameter objects for specific datatype in this study
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
        Search for annotation data with this study and return it.

        :param platform: platform id to look for in this study.
        :return: an Annotations object or nothing.
        """
        annotations = []
        for key, annotation_object in self.Annotations.__dict__.items():
            if annotation_object.platform == platform:
                annotations.append(annotation_object)

        if not annotations:
            CPrint.warn('Platform {} not found in study.'.format(platform))

        elif len(annotations) == 1:
            return annotations[0]

        else:
            CPrint.error('Duplicate platform objects found for {}: {}').format(platform,
                                                                               annotations)

    def __str__(self):
        statement = "Study object: {}".format(self.params_path)
        return statement

    def __repr__(self):
        return '<tmtk.Study> ({})'.format(self.study_folder)

    def validate_all(self, verbosity: int = 2):
        """
        Validate all items in this study.

        :param verbosity: set the verbosity of output, pick 0, 1, 2, 3 or 4.
        :return: True if everything is okay, else return False.
        """
        for obj in self.get_objects_with_prop('validate'):
            obj.validate(verbosity=verbosity)

    def files_with_changes(self):
        """Find dataframes that have changed since they have been loaded."""
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
        :return: generator for the found objects.
        """

        recursion_items = ['parent', '_parent', 'obj']

        def iterate_items(d, prop):
            for key, obj in d.items():
                if hasattr(obj, '__dict__') and key not in recursion_items:
                    yield from iterate_items(obj.__dict__, prop)

                if hasattr(obj, prop):
                    yield obj

        return {i for i in iterate_items(self.__dict__, prop)}

    @property
    def study_id(self) -> str:
        """The study ID as it is set in study params."""
        study_params = self.find_params_for_datatype('study')[0]
        return study_params.get('STUDY_ID')

    @property
    def study_name(self) -> str:
        """The study name, extracted from study param TOP_NODE."""
        study_params = self.find_params_for_datatype('study')[0]
        return study_params.get('TOP_NODE', '').split('\\')[-1]

    def call_boris(self):
        """
        Launch The Arborist GUI editor for the concept tree. This starts a
        Flask webserver in an IFrame when running in a Jupyter Notebook.

        While The Arborist is opened, the GIL prevents any other actions.
        """
        arborist.call_boris(self)

    @property
    def subject_sample_mappings(self):
        """All subject sample mapping object in this study."""
        return self.HighDim.subject_sample_mappings if hasattr(self, 'HighDim') else []

    @property
    def concept_tree(self):
        """ConceptTree object for this study."""
        return arborist.create_tree_from_study(self)

    @property
    def concept_tree_json(self):
        """Stringified JSON that is used by JSTree in The Arborist."""
        return arborist.create_concept_tree(self)

    def concept_tree_to_clipboard(self):
        """Send stringified JSON that is used by JSTree in The Arborist to clipboard."""
        ct = arborist.create_tree_from_study(self)
        return ct.jstree.to_clipboard()

    def update_from_treefile(self, treefile):
        """
        Give path to a treefile (from Boris as a Service or otherwise) and update the current
        study to match made changes.

        :param treefile: path to a treefile (stringified JSON).
        """
        with open(treefile, 'r') as f:
            json_data = json.loads(f.read())
            arborist.update_study_from_json(self, json_data)

    def update_from_baas(self, url, username=None):
        """
        Give url to a tree in BaaS.

        :param url: url that has both the study and version of a tree in BaaS
            (e.g. http://transmart-arborist.thehyve.nl/trees/study-name/1/~edit/).
        :param username: if no username is given, you will be prompted for one.
        """
        json_data = arborist.get_json_from_baas(url, username)
        arborist.update_study_from_json(self, json_data)

    def publish_to_baas(self, url, study_name=None, username=None):
        """
        Publishes a tree on a Boris as a Service instance.

        :param url: url to a instance (e.g. http://transmart-arborist.thehyve.nl/).
        :param study_name: a nice name.
        :param username: if no username is given, you will be prompted for one.
        :return: the url that points to the study you've just uploaded.
        """
        study_name = study_name or self.study_name or input('Enter study name:')
        json_data = self.concept_tree.jstree.json_data_string
        new_url = arborist.publish_to_baas(url, json_data, study_name, username)
        return HTML('<a target="_blank" href="{l}">{l}</a>'.format(l=new_url))

    def add_metadata(self):
        """Create the Tags object for this study.  Does nothing if it is already present."""
        if hasattr(self, 'Tags'):
            CPrint.okay("Study metadata tags found.")
            return

        params_path = os.path.join(self.study_folder, 'tags', 'tags.params')
        self.Params.add_params(params_path, parameters={'TAGS_FILE': 'tags.txt'})
        tag_param = self.find_params_for_datatype('tags')[0]
        self.Tags = MetaDataTags(params=tag_param, parent=self)

    def write_to(self, root_dir, overwrite=False):
        """
        Write this study to a new directory on file system.

        :param root_dir: the base directory to write the study to.
        :param overwrite: set this to True to overwrite existing files.
        """
        root_dir = os.path.expanduser(root_dir)

        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            os.makedirs(root_dir, exist_ok=True)

        for obj in self.get_objects_with_prop('path'):
            # Strip sub_path from leading slash, as os.path.join() will think its an absolute path
            sub_path = obj.path.split(self.study_folder)[1].strip('/')
            new_path = os.path.join(root_dir, sub_path)
            CPrint.info("Writing file to {}".format(new_path))
            obj.write_to(new_path, overwrite=overwrite)

    def add_clinical(self, clinical_params):
        """
        Add clinical data to a study object.

        :param clinical_params: `tmkt.ClinicalParams` object
        """
        if clinical_params.datatype != 'clinical':
            CPrint.error('Expected clinical params, but got {} params.'.format(clinical_params))
        elif self.Clinical:
            CPrint.error('Trying to add Clinical, but already there.')
        else:
            self.Clinical = Clinical(clinical_params)
