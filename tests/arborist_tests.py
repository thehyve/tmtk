import tmtk
import unittest


class ArboristTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/valid_study/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_study_load(self):
        assert self.study.params_path

    def test_create_json_string(self):
        assert self.study.Clinical.WordMapping.df.shape == (3, 4)
        json_data = tmtk.arborist.create_concept_tree(self.study)
        json_data = json_data.replace('"text": "SW48"', '"text": "SW48_MAPPED"')
        tmtk.arborist.update_study_from_json(self.study, json_data)
        assert self.study.Clinical.WordMapping.df.shape == (4, 4)
        assert '"text": "SW48_MAPPED"' in self.study.concept_tree.jstree.json_data_string


if __name__ == '__main__':
    unittest.main()
