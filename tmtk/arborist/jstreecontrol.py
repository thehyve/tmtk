import json
import pandas as pd
import tmtk
from ..utils import CPrint, Mappings, Exceptions, path_join


def create_concept_tree(column_object):
    """

    :param column_object: tmtk.Study object, tmtk.Clinical object, or ColumnMapping dataframe
    :return: json string to be interpreted by the JSTree
    """
    if isinstance(column_object, tmtk.Study):
        concept_tree = create_tree_from_study(column_object)

    elif isinstance(column_object, pd.DataFrame):
        concept_tree = create_tree_from_df(column_object)

    elif isinstance(column_object, tmtk.Clinical):
        concept_tree = create_tree_from_clinical(column_object)

    else:
        raise Exceptions.DatatypeError(type(column_object), "tmtk.Study, tmtk.Clinical or pd.DataFrame")

    return concept_tree.jstree.json_data_string


def create_tree_from_study(study_object, concept_tree=None):
    """

    :param study_object:
    :param concept_tree:
    :return:
    """
    if not concept_tree:
        concept_tree = ConceptTree()

    concept_tree = create_tree_from_clinical(study_object.Clinical, concept_tree)

    for map_file in study_object.subject_sample_mappings:
        for md5, path in map_file.get_concept_paths.items():
            concept_tree.add_node(path, concept_id=md5, node_type='highdim')

    if hasattr(study_object, 'Tags'):
        for path, tags_dict in study_object.Tags.get_tags():
            # Add TAGS string to path name, TAGS will be subnode of the concept
            # that has the meta data.
            path_in_tree = path_join(path, Mappings.tags_node_name)
            data_args = {'tags': tags_dict}
            concept_tree.add_node(path_in_tree, node_type='tag', data_args=data_args)

    return concept_tree


def create_tree_from_clinical(clinical_object, concept_tree=None):
    """

    :param clinical_object:
    :param concept_tree:
    :return:
    """
    if not concept_tree:
        concept_tree = ConceptTree()

    for var_id in clinical_object.ColumnMapping.ids:
        variable = clinical_object.get_variable(var_id)
        data_args = variable.column_map_data
        concept_path = variable.concept_path
        categories = variable.word_map_dict if not variable.is_numeric else {}

        if categories:
            node_type = 'categorical'
        else:
            node_type = 'empty' if variable.is_empty else 'numeric'

        # Store node type in `data` so it can be changed back after renaming OMIT
        data_args.update({'ctype': node_type})

        # Add filename to SUBJ_ID and OMIT, this is a work around for unique path constraint.
        if concept_path.endswith(("SUBJ ID", "OMIT")):
            concept_path = concept_path.replace("SUBJ ID", "SUBJ_ID")
            node_type = 'codeleaf'
            concept_path += ' ({})'.format(var_id)

        # Add categorical values to concept tree (if any)
        for i, datafile_value in enumerate(categories):
            oid = '{}_{}'.format(var_id, i)
            mapped = categories[datafile_value]
            mapped = mapped if not pd.isnull(mapped) else ''
            categorical_path = path_join(concept_path, mapped)
            concept_tree.add_node(categorical_path, oid,
                                  node_type='alpha',
                                  data_args={Mappings.df_value_s: datafile_value})

        concept_tree.add_node(concept_path, var_id,
                              node_type=node_type, data_args=data_args)

    return concept_tree


def create_tree_from_df(df, concept_tree=None):
    """

    :param df:
    :param concept_tree:
    :return:
    """
    if not concept_tree:
        concept_tree = ConceptTree()

    col_map_tuples = df.apply(get_concept_node_from_df, axis=1)

    for concept_path, var_id, data_args in col_map_tuples:
        concept_tree.add_node(concept_path, var_id, data_args=data_args)
    return concept_tree


def get_concept_node_from_df(x):
    """
    This is only used when a the arborist is called from a single DF.
    :param x: row in column mapping dataframe
    :return:
    """
    concept_path = path_join(x[1], x[3])
    var_id = "{}__{}".format(x[0], x[2])

    data_args = {}
    for i, s in enumerate(Mappings.column_mapping_s):
        if s in [Mappings.cat_cd_s, Mappings.data_label_s]:
            continue
        data_args.update({s: x[i] if len(x) > i else None})
    return concept_path, var_id, data_args


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

        if json_data:
            if type(json_data) == str:
                json_data = json.loads(json_data)
            self._extract_node_list(json_data)

    def add_node(self, path, concept_id=None, node_type=None, data_args=None):
        """
        Add ConceptNode object nodes list.

        :param path: Concept path for this node.
        :param concept_id: Unique ID that allows to keep track of a node.
        # :param categories: a dict of values in this categorical concept node.
        If None, this concept node is considered to be numerical unless specified otherwise.
        :param node_type: Explicitly set node type (highdim, numerical, categorical)
        :param data_args: Any additional parameters are put a 'data' dictionary.
        """

        # Check if node already exists.
        if any([str(node) == path for node in self.nodes]):
            CPrint.error('Trying to add duplicate to ConceptTree: {}\n'
                         'This fails in the GUI.'.format(path))

        new_node = ConceptNode(path,
                               concept_id=concept_id,
                               node_type=node_type,
                               data_args=data_args)
        self.nodes.append(new_node)

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
        """

        :return:
        """

        high_dim_paths = {}
        for node in self.nodes:
            if node.type == 'highdim':
                high_dim_paths[node.concept_id] = node.path
        return high_dim_paths

    @property
    def word_mapping(self):

        all_mappings = [self._extract_word_mapping_row(node) for node in self.nodes]
        df = pd.concat(all_mappings, axis=1).T

        # Fillna needs to happen because for some reason this expression below
        # returns True for NaN and NaN, which introduces unnecessary rows in word mapping.
        # This issue might need to be resolved earlier in the ConceptTree!
        changed_values = df.fillna('').ix[:, 2] != df.fillna('').ix[:, 3]

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
        if node.type not in ['numeric', 'categorical', 'codeleaf', 'empty']:
            return
        filename = node.data.get(Mappings.filename_s)
        full_path = node.path.replace(' ', '_')

        *path, data_label = full_path.rsplit(Mappings.path_delim, 1)
        path = path[0] if path else '/'

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
            # Strip last node (Meta data tags node label)
            path = node.path.rsplit(Mappings.path_delim, 1)[0]
            # Tag paths need to start with slash
            path = '\\' + path.replace(Mappings.path_delim, '\\')
            for title, desc_weight in tags_dict.items():
                description, weight = desc_weight

                if not all([title, description, weight]):
                    continue

                list_of_rows.append([path, title, description, weight])
        return list_of_rows

    @staticmethod
    def _extract_word_mapping_row(node):
        if node.type == 'alpha':
            var_id = node.concept_id.rsplit('_', 1)[0]
            filename, column = var_id.rsplit('__', 1)
            datafile_value = node.data.get(Mappings.df_value_s)
            mapped_value = node.path.rsplit(Mappings.path_delim, 1)[1]
            return pd.Series([filename, column, datafile_value, mapped_value])

    def _extract_node_list(self, json_data):
        path = []

        for node in json_data:
            self._get_children(node, path)

    def _get_children(self, node, path):
        node_type = node.get('type', 'default')
        node_children = node.get('children', [])
        node_text = node['text']

        # Check if node has metadata tag child, adds it to node list.
        meta_tag = self._get_meta_data_tags(node_children)
        if meta_tag:
            tag_path = path_join(*path, node_text, Mappings.tags_node_name)
            self.add_node(path=tag_path,
                          node_type='tag',
                          data_args=meta_tag['data'])

        if node_type in ['numeric', 'categorical', 'highdim', 'codeleaf', 'alpha', 'empty']:
            concept_path = path_join(*path, node_text)

            # node['data'].update({Mappings.cat_cd_s: category_code,
            #                      Mappings.data_label_s: node_text})

            self.add_node(path=concept_path,
                          concept_id=node.get('id'),
                          node_type=node_type,
                          data_args=node.get('data', {}),
                          )

            # If there are any alpha children, add them to ConceptTree
            for alpha in [c for c in node_children if c.get('type') == 'alpha']:
                path_to_categorical = path + [node['text']]
                self._get_children(alpha, path_to_categorical)

        elif node_type == 'default':
            path = path + [node['text']]

            for child in node_children:
                self._get_children(child, path)

    @staticmethod
    def _get_meta_data_tags(node_children):
        """
        Returns tag node if it is in children has it.
        :param node_children:
        :return:
        """
        for child in node_children:
            if child.get('type') == 'tag':
                return child


class ConceptNode:
    def __init__(self, path, concept_id=None, node_type='numeric', data_args=None):
        """
        Object to be put into a list and interpreted by JSTree.

        :param path: Concept path for this node.
        :param concept_id: Unique ID that allows to keep track of a node.
        :param categories: a list of values in this categorical concept node.
        If None, this concept node is considered to be numerical.
        :param data_args: Any additional parameters are put a 'data' dictionary.
        """
        self.path = path
        self.concept_id = concept_id
        self.data = data_args if data_args else {}
        self.type = node_type

    def __repr__(self):
        return self.path


class JSNode:
    """
    This class exists as a helper to the jsTree.  Its "json_data" method can
    generate sub-tree JSON without putting the logic directly into the jsTree.
    This data structure is only semi-immutable.  The jsTree uses a directly
    iterative (i.e. no stack is managed) builder pattern to construct a
    tree out of paths.  Therefore, the children are not known in advance, and
    we have to keep the children attribute mutable.
    """

    def __init__(self, path, oid=None, **kwargs):
        """
        kwargs allows users to pass arbitrary information into a Node that
        will later be output in json_data().  It allows for more advanced
        configuration than the default path handling that jsTree currently allows.
        For example, users may want to pass "attr" or some other valid jsTree options.
        """

        self.children = kwargs.get('children', {})
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

    def json_data(self):
        children = [self.children[k].json_data() for k in self.children]
        output = {}
        for k, v in self.__dict__.items():
            if k == 'children':
                continue
            output[k] = v
        if len(children):
            output['children'] = children
        return output


class JSTree:
    """
    An immutable dictionary-like object that converts a list of "paths"
    into a tree structure suitable for jQuery's jsTree.
    """
    def __init__(self, concept_nodes):
        """
        Take a list of paths and put them into a tree.  Paths with the same prefix should
        be at the same level in the tree.
        kwargs may be standard jsTree options used at all levels in the tree.  These will be outputted
        in the JSON.
        """

        if not all([isinstance(p, ConceptNode) for p in concept_nodes]):
            raise TypeError("All paths must be instances of {}".format(ConceptNode.__name__))

        self._root = JSNode('', None)

        # Sort paths, not sure if this is really necessary.
        concept_nodes.sort(key=lambda x: x.path)

        for node in concept_nodes:
            curr = self._root
            # sub_paths = re.split(r'[+\\]', node.path)
            sub_paths = node.path.split(Mappings.path_delim)
            data = node.__dict__.get('data', {})
            children = node.__dict__.get('_children', {})
            node_type = node.__dict__.get('type', 'default')

            # the sub paths below cause uniqueness constraint
            for i, sub_path in enumerate(sub_paths):
                if sub_path not in curr.children:
                    if i == len(sub_paths) - 1:  # Arrived at leaf
                        curr.children[sub_path] = JSNode(sub_path,
                                                         oid=node.concept_id,
                                                         data=data,
                                                         children=children,
                                                         type=node_type)
                    else:
                        curr.children[sub_path] = JSNode(sub_path)
                curr = curr.children[sub_path]

    def __repr__(self):
        """
        This outputs the tree to terminal as class representation.
        """
        return self.pretty()

    def pretty(self, root=None, depth=0, spacing=2):
        """
        Create a "pretty print" representation of the tree with customized indentation at each
        level of the tree.

        """
        if root is None:
            root = self._root
        fmt = "%s%s/" if root.children else "%s%s"
        s = fmt % (" " * depth * spacing, root.text)
        for child in sorted(root.children):
            child = root.children[child]
            s += "\n%s" % self.pretty(child, depth + 1, spacing)
        return s

    @property
    def json_data(self):
        """
        Returns a copy of the internal tree in a JSON-friendly format,
        ready for consumption by jsTree.  The data is represented as a
        list of dictionaries, each of which are our internal nodes.
        """
        return [self._root.children[k].json_data() for k in sorted(self._root.children)]

    @property
    def json_data_string(self):
        """

        :return: Returns the json_data properly formatted as string.
        """
        return json.dumps(self.json_data)

    def to_clipboard(self):
        pd.DataFrame.to_clipboard(self.json_data_string)

