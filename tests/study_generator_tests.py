import tmtk
import unittest


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.toolbox.RandomStudy(10, 5, 5)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_has_subj_id(self):
        assert 'SUBJ_ID' in self.study.concept_tree_json

    def test_study_id(self):
        assert self.study.study_id.startswith('RANDOM_STUDY_')

    def test_n_var(self):
        assert len(self.study.Clinical.all_variables) == 11

    def test_column_mapping_template_dict(self):
        assert 'Demographics' in list(self.study.Clinical.ColumnMapping.df.iloc[:, 1])
        assert 'Gender' in list(self.study.Clinical.ColumnMapping.df.iloc[:, 3])

if __name__ == '__main__':
    unittest.main()
