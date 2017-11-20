import os
import pandas as pd
import json

from ..utils import FileBase, Exceptions, Mappings
from ..params import ClinicalParams


class OntologyMapping(FileBase):
    """
    Class representing the ontology file.
    """

    def __init__(self, params=None):
        """
        Initialize by giving a params object.

        :param params: `tmtk.ClinicalParams`.
        """

        self.params = params

        if not isinstance(params, ClinicalParams):
            raise Exceptions.ClassError(type(params))
        elif params.get('ONTOLOGY_MAP_FILE'):
            self.path = os.path.join(params.dirname, params.ONTOLOGY_MAP_FILE)
        else:
            self.path = os.path.join(params.dirname, 'ontology_mapping_file.txt')
            self.params.__dict__['ONTOLOGY_MAP_FILE'] = os.path.basename(self.path)

        super().__init__()

    def create_df(self):
        """
        Create `pd.DataFrame` with a correct header.

        :return: `pd.DataFrame`.
        """
        df = pd.DataFrame(dtype=str, columns=Mappings.ontology_header)
        return df

    @property
    def concepts(self):
        return self.df.apply(lambda x: Concept(x[0], x[1], str(x[2]).split(','), x[3]),
                             axis=1)

    @property
    def tree(self):
        return OntologyTree(self.concepts)

    def as_json(self):
        return self.tree.json()


class Concept:
    def __init__(self, code, label, parents=None, blob=None):
        self.code = code
        self.label = label
        try:
            self.blob = json.loads(blob)
        except TypeError:
            self.blob = blob
        self.parents = parents
        self.children = []

    def json(self):
        return {'text': self.label,
                'id': self.code,
                'data':
                    {'blob': self.blob,
                     'code': self.code,
                     },
                'children': [child.json() for child in self.children]
                }

    def __repr__(self):
        return "{}: {}".format(self.label,
                               self.children)


class OntologyTree:
    def __init__(self, ontology_list=None):
        self.anchors = list(ontology_list)
        self.create_hierarchy()

    def _recurse_children(self, children, code):
        for term in children:
            if term.code == code:
                return term
            term_from_children = self._recurse_children(term.children, code)
            if term_from_children:
                return term_from_children

    def _find_code(self, code):
        term = self._recurse_children(self.anchors, code)
        return term

    def _iterate_hierarchy(self):
        changed = False
        for branch in self.anchors:
            for parent_code in branch.parents:

                parent = self._find_code(parent_code)

                if not parent:
                    continue

                changed = True
                try:
                    self.anchors.remove(branch)
                except ValueError:
                    # Double parents
                    pass
                parent.children.append(branch)
        return changed

    def create_hierarchy(self):
        while self._iterate_hierarchy():
            pass

    def json(self, as_object=False):
        ids_ = set()

        def clean_duplicate_ids(children):
            for term in children:
                if term.get('data', {}).get('code') in ids_:
                    term['id'] = None
                else:
                    ids_.add(term['id'])

                clean_duplicate_ids(term.get('children'))

        tree = [node.json() for node in self.anchors]
        clean_duplicate_ids(tree)
        if as_object:
            return tree
        else:
            return json.dumps(tree)

    def get_concept_rows(self):
        for node in self.json(as_object=True):
            yield from self._get_next_concept_row(node, path='')

    def _get_next_concept_row(self, node, path):

        path += '\\' + node.get('text')
        for child in node.get('children'):
            yield from self._get_next_concept_row(child, path)
        if node.get('id'):
            yield node.get('id'), path, node.get('text'), node.get('data').get('blob')
