import os

import tmtk
from tests.commons import TestBase, create_study_from_dir


class IncompletenessTests(TestBase):
    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('incomplete')

    def test_study_load(self):
        self.assertTrue(os.path.exists(self.study.params.path))

    def test_empty_wordmap(self):
        self.assertTrue(self.study.Clinical.WordMapping.validate())

    def test_non_existing_wordmap(self):
        self.study.Params.clinical.WORD_MAP_FILE = 'fake_wordmap.txt'
        self.assertTrue(self.study.Clinical.WordMapping.validate())
        self.study.Params.clinical.WORD_MAP_FILE = 'Cell-line_wordmap.txt'

    def test_update_study_from_json(self):
        json_data = tmtk.arborist.create_concept_tree(self.study)
        tmtk.arborist.update_study_from_json(self.study, json_data)

    def test_create_tags(self):
        self.study.ensure_metadata()
        self.assertTrue(self.study.Params.tags.is_viable())
        self.assertEqual(self.study.Tags.df.shape, (0, 4))
