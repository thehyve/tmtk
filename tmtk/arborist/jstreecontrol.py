import os
import re
import json


class ConceptTree:

    def __init__(self, json_data=None):
        self.nodes = []

        if json_data:
            if type(json_data) == str:
                json_data = json.loads(json_data)
            self.nodes = self._extract_node_list(json_data)

    def add_node(self, path, concept_id=None, categories: list = None, data_args=None):
        """
        Add ConceptNode object nodes list.

        :param path: Concept path for this node.
        :param concept_id: Unique ID that allows to keep track of a node.
        :param categories: a list of values in this categorical concept node.
        If None, this concept node is considered to be numerical.
        :param data_args: Any additional parameters are put a 'data' dictionary.
        """
        new_node = ConceptNode(path,
                               concept_id=concept_id,
                               categories=categories,
                               data_args=data_args)
        self.nodes.append(new_node)

    @property
    def jstree(self):
        return JSTree(self.nodes)

    def _extract_node_list(self, json_data):
        node_list = []
        path = []

        for node in json_data:
            node_list = self._get_children(node, node_list, path)

        return node_list

    def _get_children(self, node, node_list, path):
        node_type = node.get('type', 'default')
        node_children = node.get('children', [])
        node_text = node['text'].replace(' ', '_')

        if node.get('data', {}).get('Filename'):
            filename = node['data']['Filename']
            category_code = '+'.join(path).replace(' ', '_')
            column_number = int(node['data']['Column Number'])
            data_label = node_text
            concept_path = '+'.join([category_code, node_text])
            magic_col_5 = node['data'].get('Data Label Source', '')
            magic_col_6 = node['data'].get('Control Vocab Cd', '')

            categories = []
            if any([child.get('type') == 'alpha' for child in node_children]):
                categories = [child['text'] for child in node_children]

            concept_node = ConceptNode(path=concept_path ,
                                       concept_id=node['li_attr']['id'],
                                       categories=categories,
                                       data_args={'Filename': filename,
                                                  'Column Number': column_number,
                                                  'Data Label': data_label,
                                                  'Category Code': category_code,
                                                  }
                                       )

            node_list.append(concept_node)
            return node_list

        elif node_type == 'default':
            path = path + [node['text']]

            for child in node_children:
                node_list = self._get_children(child, node_list, path)
            return node_list
        else:
            return node_list


class ConceptNode:
    def __init__(self, path, concept_id=None, categories: list = None, data_args=None):
        """
        Object to be put into a list and interpreted by JSTree.

        :param path: Concept path for this node.
        :param id: Unique ID that allows to keep track of a node.
        :param categories: a list of values in this categorical concept node.
        If None, this concept node is considered to be numerical.
        :param data_args: Any additional parameters are put a 'data' dictionary.
        """
        self.path = path
        self.concept_id = concept_id

        if data_args:
            self.data = data_args

        if categories:
            self.categories = {}
            self._children = {}
            for i, cat in enumerate(categories):
                oid = '{}_{}'.format(self.concept_id, i)
                self.categories[oid] = cat
                self._children[oid] = JSNode(cat, oid, type='alpha')
                self.type = 'categorical'

        else:
            self.type = 'numeric'

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

        if oid is not None:
            li_attr = kwargs.get('li_attr', {})
            li_attr['id'] = oid
            kwargs['li_attr'] = li_attr

        self.__dict__.update(**kwargs)
        self.__dict__['text'] = path

    def json_data(self):
        children = [self.children[k].json_data() for k in self.children]
        output = {}
        for k in self.__dict__:
            if 'children' == k:
                continue
            if isinstance(self.__dict__[k], dict):
                output[k] = self.__dict__[k]
            else:
                output[k] = self.__dict__[k]
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
            sub_paths = re.split('[+/]', node.path)
            data = node.__dict__.get('data', {})
            children = node.__dict__.get('_children', {})
            node_type = node.__dict__.get('type', 'default')

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

    def find_node(self, id_):
        return self._recurse_children(self.json_data, id_)

    def _recurse_children(self, children, id_):
        for child in children:
            if child.get('li_attr', {}).get('id') == id_:  # Check if child has correct 'id' in 'li_attr' subdict.
                return child
            if child.get('children'):  # If there are children, recurse into nested dictionary
                node = self._recurse_children(child['children'], id_)
                if node:  # Only return if recursion returns something
                    return node

    def update_node(self, id_, subkey=None, **kwargs):
        node = self.find_node(id_)
        if node:
            if subkey:
                node[subkey].update(**kwargs)
            else:
                node.update(**kwargs)
