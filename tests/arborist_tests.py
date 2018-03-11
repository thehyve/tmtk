from unittest.mock import patch

import tmtk
from tmtk.utils import ArboristException

from tests.commons import TestBase, create_study_from_dir


class ArboristTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('valid_study')

    def test_create_json_string(self):
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (3, 4))
        json_data = tmtk.arborist.create_concept_tree(self.study)
        json_data = json_data.replace('"text": "SW48"', '"text": "SW48_MAPPED"')
        tmtk.arborist.update_study_from_json(self.study, json_data)
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (4, 4))
        self.assertIn('"text": "SW48_MAPPED"', self.study.concept_tree.jstree.json_data_string)
        self.study.Clinical.WordMapping.word_map_changes(silent=True)

    @patch("time.sleep", side_effect=KeyboardInterrupt)
    def test_call_boris(self, mocked_sleep):
        self.assertRaises(ArboristException, self.study.call_boris)

