from unittest.mock import patch

import os
from requests.exceptions import InvalidSchema

import tmtk
from tests.commons import TestBase, create_study_from_dir
from tmtk.arborist.jupyter_extension import TransmartArborist
from tmtk.arborist.connect_to_baas import json_url, PathError
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
                'arguments': None,
                'headers': None
            })
            self.request.arguments = {'treefile': [jsn]}
            self.request.headers = {'Referer': 'treefile={}'.format(jsn)}
            self.log = nested_namespace({
                'info': print
            })
            self.base_url = '/'
            self.finish = print
            self.render_template = self.breakpoint

        def breakpoint(self, *args, **kwargs):
            raise Breakpoint

        @staticmethod
        def get_json_body():
            return '{"test": 123}'

    return MockedRequests()


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

    def test_changes_clinical(self):
        study = create_study_from_dir('valid_study')
        json_data = self.json_data.replace('"text": "Characteristics"', '"text": "Characteristic"')
        json_data = json_data.replace('"text": "SW48"', '"text": "SW48_MAPPED"')
        tmtk.arborist.update_study_from_json(study, json_data)
        self.assertEqual(9, len(study.Clinical.show_changes()))

    @patch("time.sleep", side_effect=KeyboardInterrupt)
    def test_call_boris(self, mocked_sleep):
        self.assertRaises(ArboristException, self.study.call_boris)

    def test_publish_baas(self):
        with self.assertRaises(InvalidSchema):
            self.study.publish_to_baas('mock://mocked-arborist-host.nl', username='test')

    def test_json_url(self):
        self.assertEqual(
            'http://transmart-arborist.thehyve.nl/trees/study-name/1',
            json_url('http://transmart-arborist.thehyve.nl/trees/study-name/1/~edit/asf')
        )
        with self.assertRaises(PathError):
            json_url('http://transmart-arborist.thehyve.nl/trees/')

    def test_server_extension_get(self):
        req = create_mock_request(self.tree_file)
        with self.assertRaises(Breakpoint):
            TransmartArborist.get(req)

    def test_server_extension_post(self):
        req = create_mock_request(self.tree_file)
        TransmartArborist.post(req)
        done_file = os.path.join(os.path.dirname(self.tree_file), 'DONE')
        self.assertTrue(os.path.exists(done_file))

    def test_tree_pretty(self):
        self.study.concept_tree.jstree.__repr__()

    def test_update_highdim_paths(self):
        prot_paths = self.study.HighDim.proteomics.sample_mapping.df.cat_cd.unique
        self.assertEqual(1, len(prot_paths()))
        self.assertTrue(prot_paths()[0].endswith('MZ ratios'))
        json_data = self.json_data.replace('"text": "MZ ratios"', '"text": "Mass spec ratios"')
        tmtk.arborist.update_study_from_json(self.study, json_data)
        self.assertEqual(1, len(prot_paths()))
        self.assertTrue(prot_paths()[0].endswith('Mass spec ratios'))
