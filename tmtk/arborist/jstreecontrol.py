import json
import pandas as pd
import tmtk
import tqdm

from ..utils import Mappings, Exceptions, path_join, path_converter, Message
from ..clinical.Variable import VarID


def create_concept_tree(column_object):
    """

    :param column_object: tmtk.Study object, tmtk.Clinical object, or ColumnMapping dataframe
    :return: json string to be interpreted by the JSTree
    """
    if isinstance(column_object, tmtk.Study):
        concept_tree = create_tree_from_study(column_object)

    else:
        raise Exceptions.ClassError(type(column_object, 'tmtk.Study'))

    return concept_tree.jstree.json_data_string


def _get_hd_args(path, high_dim_node, annotation):
    """
    Create dict with meta tags that belong to a certain high dimensional node.
    """
    map_file = high_dim_node.sample_mapping

    s = map_file.slice_path(path).iloc[:, 5].unique()
    t = map_file.slice_path(path).iloc[:, 6].unique()

    hd_args = {'hd_sample': ', '.join(s.astype(str)) if pd.notnull(s[0]) else '',
               'hd_tissue': ', '.join(t.astype(str)) if pd.notnull(t[0]) else '',
               'hd_type': Mappings.annotation_data_types.get(high_dim_node.params.datatype),
               }

    if annotation:
        hd_args.update({'pl_marker_type': annotation.marker_type,
                        'pl_genome_build': annotation.params.get('GENOME_RELEASE', ''),
                        'pl_title': annotation.params.get('TITLE', ''),
                        'pl_id': annotation.platform})
    return hd_args


def create_tree_from_study(study, concept_tree=None):
    """

    :param study:
    :param concept_tree:
    :return:
    """
    if not concept_tree:
        concept_tree = ConceptTree()

    concept_tree = create_tree_from_clinical(study.Clinical, concept_tree)

    for high_dim_node in study.high_dim_files:
        annotation = study.find_annotation(high_dim_node.platform)

        for md5, path in high_dim_node.sample_mapping.get_concept_paths.items():
            path = path_converter(path, to_internal=True)
            hd_args = _get_hd_args(path, high_dim_node, annotation)
            concept_tree.add_node(path, var_id=md5, node_type='highdim',
                                  data_args={'hd_args': hd_args})

    if hasattr(study, 'Tags'):
        for i, (path, tags_dict) in enumerate(study.Tags.get_tags()):
            # Don't add empty folder if Tags are at study level
            path_in_tree = path_join(path, Mappings.tags_node_name) if path != "" else Mappings.tags_node_name
            path_in_tree = path_converter(path_in_tree, to_internal=True)
            data_args = {'tags': tags_dict}
            concept_tree.add_node(path_in_tree,
                                  var_id="tags_id_{}".format(i),
                                  node_type='tag',
                                  data_args=data_args)

    return concept_tree


def create_tree_from_clinical(clinical_object, concept_tree=None):
    """

    :param clinical_object:
    :param concept_tree:
    :return:
    """
    if not concept_tree:
        concept_tree = ConceptTree()

    column_map_ids = clinical_object.ColumnMapping.ids
    no_bar = True if len(column_map_ids) < 200 else False
    bar_format = '{l_bar}{bar} | {n_fmt}/{total_fmt} nodes ready, {rate_fmt}'

    for var_id, variable in tqdm.tqdm_notebook(clinical_object.all_variables.items(),
                                               bar_format=bar_format,
                                               unit=' nodes',
                                               leave=False,
                                               dynamic_ncols=True,
                                               disable=no_bar):
        data_args = variable.column_map_data

        # Don't need these, they're in the tree.
        for k in [Mappings.cat_cd_s, Mappings.data_label_s]:
            data_args.pop(k)
        concept_path = path_converter(variable.concept_path, to_internal=True)
        categories = {} if variable.is_numeric else variable.word_map_dict

        if categories:
            node_type = 'categorical'
        else:
            node_type = 'empty' if variable.is_empty else 'numeric'

        # Store node type in `data` so it can be changed back after renaming OMIT
        data_args.update({'ctype': node_type})

        # Store column header of variable.
        data_args.update({'dfh': variable.header})

        # Add filename to SUBJ_ID and OMIT, this is a work around for unique path constraint.
        if variable.data_label in {"SUBJ_ID", "OMIT"}:
            concept_path = concept_path.replace("SUBJ ID", "SUBJ_ID")
            node_type = 'codeleaf'

        # Add categorical values to concept tree (if any)
        for i, datafile_value in enumerate(categories):
            oid = var_id.create_category(i + 1)
            mapped = categories[datafile_value]
            mapped = mapped if not pd.isnull(mapped) else ''
            categorical_path = path_join(concept_path, mapped)
            concept_tree.add_node(categorical_path, oid,
                                  node_type='alpha',
                                  data_args={Mappings.df_value_s: datafile_value})

        concept_tree.add_node(concept_path, var_id,
                              node_type=node_type, data_args=data_args)

    return concept_tree


class ConceptTree:
    """
    Build a ConceptTree to be used in the graphical tree editor.

    """

    def __init__(self, json_data=None):
        """

        :param json_data: Optional json data that initiates the ConceptTree object
        and populates it with ConceptNode objects.
        """
        self.nodes = []
        self.paths = set()

        if json_data:
            if type(json_data) == str:
                json_data = json.loads(json_data)

                # This to get version2 concept tree
                try:
                    if json_data.get("version") == "2":
                        json_data = json_data.get('concept_tree')
                except AttributeError:
                    pass

            self._extract_node_list(json_data)

    def add_node(self, path, var_id=None, node_type=None, data_args=None):
        """
        Add ConceptNode object nodes list.

        :param path: Concept path for this node.
        :param var_id: Unique ID that allows to keep track of a node.
        :param node_type: Explicitly set node type (highdim, numerical, categorical)
        :param data_args: Any additional parameters are put a 'data' dictionary.
        """

        # Check if node already exists.
        if path in self.paths and node_type not in {'alpha', 'codeleaf'}:
            Message.warning('Trying to add duplicate to ConceptTree: {}\n'
                            'This might fail in the GUI.'.format(path))

        new_node = ConceptNode(path,
                               var_id=var_id,
                               node_type=node_type,
                               data_args=data_args)
        self.nodes.append(new_node)
        self.paths.add(new_node.path)

    @property
    def jstree(self):
        return JSTree(self.nodes)

    @property
    def column_mapping_file(self):
        """

        :return: Column Mapping file based on ConceptTree object.
        """
        df = pd.concat([self._extract_column_mapping_row(node) for node in self.nodes], axis=1).T
        df.columns = Mappings.column_mapping_header
        return df

    @property
    def high_dim_paths(self):
        """ All high dimensional nodes in concept tree as dict """
        return {node.var_id: path_converter(node.path, from_internal=True)
                for node in self.nodes if node.type == 'highdim'}

    @property
    def word_mapping(self):

        all_mappings = [self._extract_word_mapping_row(node) for node in self.nodes]
        df = pd.concat(all_mappings, axis=1).T

        # Fillna needs to happen because for some reason this expression below
        # returns True for NaN and NaN, which introduces unnecessary rows in word mapping.
        # This issue might need to be resolved earlier in the ConceptTree!
        changed_values = df.fillna('').iloc[:, 2] != df.fillna('').iloc[:, 3]

        # Set None to NaN, else empty fields in dataframes are not recognized (None != NaN)
        df.fillna(value=pd.np.nan, inplace=True)

        df.columns = Mappings.word_mapping_header
        return df[changed_values].reset_index(drop=True)

    @property
    def tags_file(self):
        all_mappings = [self._extract_node_tags(node) for node in self.nodes]

        # This reduces the nested dictionary to a flat one.
        flat_mapping = [row for nest_list in all_mappings for row in nest_list]

        column_names = Mappings.tags_header

        try:
            df = pd.concat([pd.Series(row) for row in flat_mapping], axis=1).T
            df.columns = column_names
        except ValueError:  # This happens when there are no tags in the file
            df = pd.DataFrame(columns=column_names)

        return df

    @staticmethod
    def _extract_column_mapping_row(node):
        if node.type not in {'numeric', 'categorical', 'codeleaf', 'empty'}:
            return
        filename = node.data.get(Mappings.filename_s)

        *path, data_label = node.path.rsplit(Mappings.PATH_DELIM, 1)
        path = path_converter(path[0], from_internal=True) if path else Mappings.EXT_PATH_DELIM

        # Remove file names from SUBJ_ID, they were added as workaround for unique constraints.
        if data_label.startswith("SUBJ_ID"):
            data_label = "SUBJ_ID"

        # Remove variable ID from OMIT variables.
        if data_label.startswith("OMIT"):
            data_label = "OMIT"

        column = node.data.get(Mappings.col_num_s)
        magic5 = node.data.get(Mappings.magic_5_s)
        magic6 = node.data.get(Mappings.magic_6_s)
        concept_type = node.data.get(Mappings.concept_type_s)
        new_row = pd.Series([filename, path, column, data_label, magic5, magic6, concept_type])
        if all([filename, data_label, column]):
            return new_row

    @staticmethod
    def _extract_node_tags(node):
        list_of_rows = []
        tags_dict = node.data.get('tags', {})
        if tags_dict:

            # Tag paths need to start with slash
            path = node.path.rsplit(Mappings.tags_node_name, 1)[0].strip(Mappings.PATH_DELIM)
            path = path_converter(path, from_internal=True)
            path = Mappings.EXT_PATH_DELIM + path

            for title, (description, weight, *_) in tags_dict.items():
                if not all([title, description, weight]):
                    continue

                list_of_rows.append([path, title, description, weight])
        return list_of_rows

    @staticmethod
    def _extract_word_mapping_row(node):
        if node.type == 'alpha':
            filename, column, c = node.var_id
            datafile_value = node.data.get(Mappings.df_value_s)
            mapped_value = node.path.rsplit(Mappings.PATH_DELIM, 1)[1]
            return pd.Series([filename, column, datafile_value, mapped_value])

    def _extract_node_list(self, json_data):
        path = []

        for node in json_data:
            self._get_children(node, path)

    def _get_children(self, node, path):
        node_type = node.get('type', 'default')
        node_children = node.get('children', [])
        node_text = node['text']
        node_path = path + [node_text]

        if node_type != 'default':

            concept_path = path_join(*node_path)

            var_id = VarID(node.get('id')) if node_type != 'tag' else None

            self.add_node(path=concept_path,
                          var_id=var_id,
                          node_type=node_type,
                          data_args=node.get('data', {}),
                          )

        for child in node_children:
            self._get_children(child, node_path)


class ConceptNode:
    def __init__(self, path, var_id=None, node_type='numeric', data_args=None):
        """
        Object to be put into a list and interpreted by JSTree.

        :param path: Concept path for this node.
        :param var_id: Unique ID that allows to keep track of a node.
        :param node_type: If None, this concept node is considered to be numerical.
        :param data_args: Any additional parameters are put a 'data' dictionary.
        """
        self.path = path
        self.var_id = var_id
        self.data = data_args if data_args else {}
        self.type = node_type

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.path


class JSNode:
    """
    This class exists as a helper to the JSTree.  Its "json_data" method can
    generate sub-tree JSON without putting the logic directly into the JSTree.
    """

    def __init__(self, path, oid=None, **kwargs):
        """
        kwargs allows users to pass arbitrary information into a Node that
        will later be output in json_data().  It allows for more advanced
        configuration than the default path handling that jsTree currently allows.
        For example, users may want to pass "attr" or some other valid jsTree options.
        """

        self.children = {}
        self.helper_children = {}
        if not all([isinstance(self.children[child], JSNode) for child in self.children]):
            raise TypeError("One or more children were not instances of '{}'".format(JSNode))
        if 'children' in kwargs:
            del kwargs['children']

        self.data = kwargs.get('data', {})
        if self.data:
            del kwargs['data']

        self.__dict__.update(id=oid)

        self.__dict__.update(**kwargs)
        self.__dict__['text'] = path

    def get_child(self, var_id, text):
        return self.children.get(var_id) or self.helper_children.get(text) or self.children.get(text)

    def __repr__(self):
        return self.text

    def json_data(self):
        children = [k.json_data() for k in self.children.values()]
        output = {}
        for k, v in self.__dict__.items():
            if k in {'children', 'helper_children'}:
                continue
            output[k] = v
        if children:
            output['children'] = children
        return output


class JSTree:
    """
    An json like object that converts a list of nodes into something
    that jQuery jstree can use.
    """

    def __init__(self, concept_nodes):
        """
        Take a list of paths and put them into a tree.
        """

        if not all([isinstance(p, ConceptNode) for p in concept_nodes]):
            raise TypeError("All paths must be instances of {}".format(ConceptNode.__name__))

        self._root = JSNode('', None)

        # Sort paths, not sure if this is really necessary.
        concept_nodes.sort(key=lambda x: x.path)

        for node in concept_nodes:
            curr = self._root
            sub_paths = node.path.split(Mappings.PATH_DELIM)
            data = node.__dict__.get('data', {})
            node_type = node.__dict__.get('type', 'default')

            # Will be used to add the categories to the right categorical node.
            parent = node.var_id.parent if node_type == 'alpha' else 0

            # And now for the tricky bit.
            for i, sub_path in enumerate(sub_paths):

                # Arrived at leaf.  Add final JSNode of path and give it the VarID
                if i == len(sub_paths) - 1:  # Arrived at leaf
                    new_node = JSNode(sub_path,
                                      oid=node.var_id,
                                      data=data,
                                      type=node_type)

                    curr.children[node.var_id] = new_node
                    curr.helper_children[new_node.text] = new_node
                    continue  # next path

                # Not a leaf, check if current path already in tree.
                next_child = curr.get_child(var_id=parent, text=sub_path)

                if not next_child:
                    new_node = JSNode(sub_path)
                    curr.children[sub_path] = new_node
                    curr = new_node

                else:
                    curr = next_child

    def __repr__(self):
        """
        This outputs the tree to terminal as class representation.
        """
        return self.pretty()

    def pretty(self, root=None, depth=0, spacing=2):
        """
        Create a pretty representation of tree.
        """
        if root is None:
            root = self._root
        fmt = "%s%s/" if root.children else "%s%s"
        s = fmt % (" " * depth * spacing, root.text)
        for child in root.children.values():
            s += "\n%s" % self.pretty(child, depth + 1, spacing)
        return s

    @property
    def json_data(self):
        """
        Convert this object to json ready to be consumed by jstree.
        """
        return [k.json_data() for k in self._root.children.values()]

    @property
    def json_data_string(self):
        """

        :return: Returns the json_data properly formatted as string.
        """
        return json.dumps(self.json_data, cls=MyEncoder)

    def to_clipboard(self):
        pd.DataFrame.to_clipboard(self.json_data_string)


class MyEncoder(json.JSONEncoder):
    """ Overwriting the standard JSON Encoder to treat numpy ints as native ints."""

    def default(self, obj):
        if isinstance(obj, (pd.np.int64, pd.np.int32)):
            return int(obj)
        elif isinstance(obj, VarID):
            return str(obj)
        else:
            return super(MyEncoder, self).default(obj)
