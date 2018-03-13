from unittest.mock import patch

import os
from requests.exceptions import InvalidSchema

import tmtk
from tests.commons import TestBase, create_study_from_dir
from tmtk.arborist.jupyter_extension import TransmartArborist
from tmtk.utils import ArboristException


class Breakpoint(Exception):
    pass


def nested_namespace(nested_dict=None):
    class Namespace:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                if type(v) == dict:
                    kwargs[k] = Namespace(**v)
            self.__dict__ = kwargs

    return Namespace(**nested_dict)


def create_mock_request(jsn):
    class MockedRequests:
        def __init__(self):
            self.request = nested_namespace({
                'arguments': None
            })
            self.request.arguments = {'treefile': [jsn]}
            self.log = nested_namespace({
                'info': print
            })
            self.base_url = '/'
            self.finish = print
            self.render_template = self.breakpoint

        def breakpoint(self, *args, **kwargs):
            raise Breakpoint

    return MockedRequests()


req = create_mock_request('hoi')


class ArboristTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('valid_study')
        cls.tree_file = os.path.join(cls.temp_dir, 'treefile.json')
        cls.json_data = tmtk.arborist.create_concept_tree(cls.study)

        with open(cls.tree_file, 'w') as f:
            f.write(cls.json_data)

    def test_changes_word_mapping(self):
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (3, 4))
        json_data = self.json_data.replace('"text": "SW48"', '"text": "SW48_MAPPED"')
        tmtk.arborist.update_study_from_json(self.study, json_data)
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (4, 4))
        self.assertIn('"text": "SW48_MAPPED"', self.study.concept_tree.jstree.json_data_string)
        self.assertEqual(1, len(self.study.Clinical.WordMapping.word_map_changes(silent=True)))

    def test_changes_column_mapping(self):
        json_data = self.json_data.replace('"text": "Characteristics"', '"text": "Characteristic"')

        with open(self.tree_file, 'w') as f:
            f.write(json_data)

        self.study.update_from_treefile(self.tree_file)
        self.assertEqual(8, len(self.study.Clinical.ColumnMapping.path_changes(silent=True)))

    @patch("time.sleep", side_effect=KeyboardInterrupt)
    def test_call_boris(self, mocked_sleep):
        self.assertRaises(ArboristException, self.study.call_boris)

    def test_publish_baas(self):
        with self.assertRaises(InvalidSchema):
            self.study.publish_to_baas('mock://mocked-arborist-host.nl', username='test')

    def test_server_extension_get(self):
        req = create_mock_request(self.tree_file)
        with self.assertRaises(Breakpoint):
            TransmartArborist.get(req)
