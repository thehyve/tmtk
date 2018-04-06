import os
import json
from IPython.display import HTML
import tempfile

from .clinical import Clinical
from .params import Params, ParamsBase
from .highdim import HighDim
from .annotation import Annotations
from .tags import MetaDataTags
from .utils import Mappings, TransmartBatch, ValidateMixin, FileBase
from tmtk import utils, arborist

from itertools import chain


class Study(ValidateMixin):
    """
    Describes an entire TranSMART study.  This is the main object used
    in tmtk. Studies can be initialized by pointing to a study.params file.
    This study has to be structured according to specification for
    transmart-batch.

    >>> import tmtk
    >>> study = tmtk.Study('./studies/valid_study/study.params')

    This will create the study object which can be used as a starting point
    for custom curation or directly in The Arborist.

    To use the more limited 16.2 data model with transmart-batch set this option
    before creating this object.

    >>> tmtk.options.transmart_batch_mode = True
    """

    def __init__(self, study_params_path=None, minimal=False):
        """
        Studies can be initialized by pointing to a study.params file.

        :param study_params_path: valid path to a study.params.
        :param minimal: if True, tmtk will only load parameter files.
        """
        if not study_params_path:
            self.study_folder = tempfile.mkdtemp(prefix='tmtk-')
            self.Params = Params(self.study_folder)
            self.Params.add_params(os.path.join(self.study_folder, 'study.params'))

        elif os.path.basename(study_params_path) != 'study.params':
            raise utils.PathError('Please give a path to study.params file, or None to make one in tmp.')

        else:
            self.study_folder = os.path.dirname(os.path.abspath(study_params_path))
            self.Params = Params(self.study_folder)

        self.params = self.find_params_for_datatype('study')[0]

        if minimal:
            return

        # Look for clinical params and create child object
        self.Clinical = Clinical()
        clinical_params = self.find_params_for_datatype(datatypes='clinical')
        if clinical_params:
            self.Clinical.params = clinical_params[0]
        else:
            self.create_clinical()

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

    def __str__(self):
        return 'StudyObject ({})'.format(self.study_folder)

    def __repr__(self):
        return 'StudyObject ({})'.format(self.study_folder)

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
        if not hasattr(self, 'Annotations'):
            self.msgs.warning('No annotations found for this study.')
            return

        annotations = []
        for key, annotation_object in self.Annotations.__dict__.items():
            if annotation_object.platform == platform:
                annotations.append(annotation_object)

        if not annotations:
            self.msgs.warning('Platform {} not found in study.'.format(platform))

        elif len(annotations) == 1:
            return annotations[0]

        else:
            self.msgs.error('Duplicate platform objects found for {}: {}').format(platform, annotations)

    def files_with_changes(self, ):
        """Find dataframes that have changed since they have been loaded."""
        return [obj for obj in self.all_files if obj.df_has_changed]

    def get_objects(self, of_type):
        """
        Search for objects that have inherited from a certain type.

        :param of_type: type to match against.
        :return: generator for the found objects.
        """

        recursion_items = ['parent', '_parent', 'obj', 'msgs']

        def iterate_items(d):
            for key, obj in d.items():
                if hasattr(obj, '__dict__') and key not in recursion_items:
                    yield from iterate_items(obj.__dict__)

                if isinstance(obj, of_type):
                    yield obj

        return {i for i in iterate_items(self.__dict__)}

    @property
    def study_id(self) -> str:
        """The study ID as it is set in study params."""
        return self.params.get('STUDY_ID')

    @study_id.setter
    def study_id(self, value):
        setattr(self.params, 'STUDY_ID', value.upper())
        for obj in self.sample_mapping_files:
            obj.study_id = value.upper()

    @property
    def study_name(self) -> str:
        """The study name, extracted from study param TOP_NODE."""
        return self.params.get('TOP_NODE', self.study_id).strip('\\').rsplit('\\', 1)[-1]

    @study_name.setter
    def study_name(self, value):
        container = '\\'.join(self.top_node.strip('\\').split('\\')[:-1])
        self.top_node = "\\{}\\{}".format(container, value)

    @property
    def study_blob(self):
        """
        JSON data that can be loaded in the study blob. This will be added
        as a separate file next to the study.params. The STUDY_JSON_BLOB
        parameter will be set to point to this file.
        """

        if self.params.json_blob:
            return self.params.json_blob

        blob_param = self.params.get('STUDY_JSON_BLOB')
        if blob_param:
            with open(os.path.join(self.study_folder, blob_param), 'r') as f:
                self.params.json_blob = json.load(f)
                return self.params.json_blob

    @study_blob.setter
    def study_blob(self, value):
        blob_param = self.params.get('STUDY_JSON_BLOB')
        if not blob_param:
            self.params.set('STUDY_JSON_BLOB', 'study_blob.json')

        self.params.json_blob = value

    @property
    def top_node(self) -> str:
        if self.params.get('TOP_NODE'):
            return self.params.get('TOP_NODE')

        pub_priv = 'Private Studies' if self.security_required else 'Public Studies'
        return "\\{}\\{}".format(pub_priv, self.study_id)

    @top_node.setter
    def top_node(self, value: str):
        setattr(self.params, 'TOP_NODE', value)

    @property
    def security_required(self) -> bool:
        return self.params.get('SECURITY_REQUIRED', 'Y') == 'Y'

    @security_required.setter
    def security_required(self, value: bool):
        assert value in (True, False)
        setattr(self.params, 'SECURITY_REQUIRED', 'Y' if value else 'N')
        # Reset Public/Private in TOP_NODE
        top = self.params.get('TOP_NODE', '')
        if top.startswith('\\Public Studies\\') or top.startswith('\\Private Studies\\'):
            pub_priv = ('Public Studies', 'Private Studies')
            old, new = pub_priv if value else reversed(pub_priv)
            self.top_node = self.top_node.replace(old, new)

    def call_boris(self, height=650):
        """
        Launch The Arborist GUI editor for the concept tree. This starts a
        Flask webserver in an IFrame when running in a Jupyter Notebook.

        While The Arborist is opened, the GIL prevents any other actions.
        :param height: set the height of the output cell
        """
        arborist.call_boris(self, height=height)

    @property
    def high_dim_files(self):
        """All high dimensional file objects in this study."""
        return self.HighDim.high_dim_files if hasattr(self, 'HighDim') else []

    @property
    def sample_mapping_files(self):
        """All subject sample mapping file objects in this study."""
        return self.HighDim.sample_mapping_files if hasattr(self, 'HighDim') else []

    @property
    def annotation_files(self):
        """All annotation file objects in this study."""
        return self.Annotations.annotation_files if hasattr(self, 'Annotations') else []

    @property
    def clinical_files(self):
        """All clinical file objects in this study."""
        return self.Clinical.clinical_files if hasattr(self.Clinical, 'clinical_files') else []

    @property
    def tag_files(self):
        return [self.Tags] if hasattr(self, 'Tags') else []

    @property
    def all_files(self):
        """All file objects in this study."""
        return self.high_dim_files + self.sample_mapping_files + self.annotation_files + self.clinical_files + self.tag_files

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

    def ensure_metadata(self):
        """Create the Tags object for this study.  Does nothing if it is already present."""
        if hasattr(self, 'Tags'):
            self.msgs.okay("Study metadata tags found.")
            return

        p = os.path.join(self.study_folder, 'tags', 'tags.params')
        self.Params.add_params(p, parameters={'TAGS_FILE': 'tags.txt'})
        tag_param = self.find_params_for_datatype('tags')[0]
        self.Tags = MetaDataTags(params=tag_param, parent=self)

    def write_to(self, root_dir, overwrite=False, return_new=True):
        """
        Write this study to a new directory on file system.

        :param root_dir: the base directory to write the study to.
        :param overwrite: set this to True to overwrite existing files.
        :param return_new: if True load the study object from the new location and return it.
        :return: new study object if return_new == True.
        """
        root_dir = os.path.expanduser(root_dir)

        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            os.makedirs(root_dir, exist_ok=True)

        for obj in chain(self.get_objects(FileBase), self.get_objects(ParamsBase)):
            # Strip sub_path from leading slash, as os.path.join() will think its an absolute path
            sub_path = obj.path.split(self.study_folder)[1].strip(os.sep)
            new_path = os.path.join(root_dir, sub_path)
            self.msgs.info("Writing file to {}".format(new_path))
            obj.write_to(new_path, overwrite=overwrite)

        if return_new:
            return Study(os.path.join(root_dir, 'study.params'))

    def create_clinical(self):
        """ Add clinical data to a study object by creating empty params. """

        if self.find_params_for_datatype('clinical'):
            self.msgs.error('Trying to add Clinical, but already there.')
        else:
            new_path = os.path.join(self.study_folder, 'clinical', 'clinical.params')
            self.Clinical.params = self.Params.add_params(new_path)

    def apply_blueprint(self, blueprint, omit_missing=False):
        """
        Apply a blueprint to current study.

        :param blueprint: blueprint object (e.g. dictionary) or link to blueprint json on disk.
        :param omit_missing: if True, then variable that are not present in the blueprint
        will be set to OMIT.
        """

        if isinstance(blueprint, str) and os.path.exists(blueprint):
            with open(blueprint) as f:
                blueprint = json.load(f)

        self.Clinical.apply_blueprint(blueprint, omit_missing)
        self.ensure_metadata()
        self.Tags.apply_blueprint(blueprint)

    @property
    def load_to(self):
        if self.files_with_changes():
            self.msgs.error('Files with changes found, they will not be loaded! Save them before restarting the job!')
        return TransmartBatch(param=self.params.path,
                              items_expected=self._study_total_batch_items,
                              ).get_loading_namespace()

    @property
    def _study_total_batch_items(self):
        """A dictionary of with params path with number of items to be written."""

        lazy_dict = {}

        for item in self._get_loadable_objects():
            lazy_dict.update(item._get_lazy_batch_items())
        return lazy_dict

    def _get_loadable_objects(self):
        """ Gets all items that could potentially be loaded with transmart-batch """
        l = self.high_dim_files + self.annotation_files + self.tag_files
        if hasattr(self, 'Clinical'):
            l.append(self.Clinical)
        return l

    def get_object_from_params_path(self, path):
        """ Returns object that belongs to the params path given """
        for item in self._get_loadable_objects():
            if item.params.path == path:
                return item

    def validate_all(self, verbosity='WARNING'):
        """
        Validate all items in this study.

        :param verbosity: only display output of this level and above.
            Levels: 'debug', 'info', 'okay', 'warning', 'error', 'critical'.
            Default is 'WARNING'.
        :return: True if no errors or critical is encountered.
        """
        return all([obj.validate(verbosity=verbosity) for obj in self.get_objects(ValidateMixin)])

    def _validate_study_id(self):
        if bool(self.study_id):
            self.msgs.okay('Study ID found: {!r}'.format(self.study_id))
        else:
            self.msgs.error('Invalid study id: {!r}'.format(self.study_id))

    def _validate_study_params_on_disk(self):
        """ Validate whether study params exists on disk. """
        if os.path.exists(self.params.path):
            self.msgs.okay('Study params found on disk.')
        else:
            self.msgs.error('Study params not on disk.')

    def get_dimensions(self):
        """ Returns a list of dimensions applicable to study """
        dimensions = ['study', 'concept', 'patient']

        if self.Clinical.find_variables_by_label('START_DATE'):
            dimensions.append('start time')

        if self.Clinical.find_variables_by_label('TRIAL_VISIT_LABEL'):
            dimensions.append('trial visit')

        _mods_found = set()

        for modifier in self.Clinical.find_variables_by_label('MODIFIER'):

            if modifier.modifier_code in _mods_found:
                continue
            _mods_found.add(modifier.modifier_code)

            try:
                mod_name = self.Clinical.Modifiers.df.loc[modifier.modifier_code,
                                                          self.Clinical.Modifiers.df.columns[2]]
                dimensions.append(mod_name)
            except KeyError:
                self.msgs.error('Cannot retrieve modifier {!r}, as it is not in modifiers file.'.format(modifier))
                raise

        return dimensions
