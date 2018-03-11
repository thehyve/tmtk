import tmtk
from tests.commons import TestBase


class GeneratorTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = tmtk.toolbox.RandomStudy(10, 5, 5)

    def test_has_subj_id(self):
        self.assertIn('SUBJ_ID', self.study.concept_tree_json)

    def test_study_id(self):
        self.assertTrue(self.study.study_id.startswith('RANDOM_STUDY_'))

    def test_n_var(self):
        self.assertEqual(len(self.study.Clinical.all_variables), 11)

    def test_column_mapping_template_dict(self):
        self.assertIn('Demographics', list(self.study.Clinical.ColumnMapping.df.iloc[:, 1]))
        self.assertIn('Gender', list(self.study.Clinical.ColumnMapping.df.iloc[:, 3]))

    def test_export_to_skinny(self):
        export = tmtk.toolbox.SkinnyExport(self.study)
        export.build_observation_fact()
        self.assertGreater(export.observation_fact.df.shape[0], 1)
