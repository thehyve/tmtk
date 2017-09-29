import tmtk
import unittest


class IncompletenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/incomplete/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_study_load(self):
        assert self.study.params.path

    def test_empty_wordmap(self):
        assert self.study.Clinical.WordMapping.validate()

    def test_non_existing_wordmap(self):
        self.study.Params.clinical.WORD_MAP_FILE = 'fake_wordmap.txt'
        assert self.study.Clinical.WordMapping.validate()
        self.study.Params.clinical.WORD_MAP_FILE = 'Cell-line_wordmap.txt'

    def test_create_json_string(self):
        assert tmtk.arborist.create_concept_tree(self.study)

    def test_update_study_from_json(self):
        json_data = tmtk.arborist.create_concept_tree(self.study)
        tmtk.arborist.update_study_from_json(self.study, json_data)

    def test_create_tags(self):
        self.study.ensure_metadata()
        assert self.study.Params.tags.is_viable()
        assert self.study.Tags.df.shape == (0, 4)


if __name__ == '__main__':
    unittest.main()
