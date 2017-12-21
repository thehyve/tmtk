import tmtk
import unittest
import tempfile
import shutil


class SkinnyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/TEST_17_1/study.params')
        cls.temp_dir = tempfile.mkdtemp()
        cls.export = tmtk.toolbox.SkinnyExport(cls.study, cls.temp_dir)
        cls.export.build_observation_fact()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        pass

    def test_update_instance_num(self):
        export_df = self.export.observation_fact.df[self.export.observation_fact.primary_key]
        assert export_df.duplicated().sum() == 0

    def test_row_wide_modifiers(self):
        assert 'TRANSMART:SAMPLE_CODE' in set(self.export.observation_fact.df.modifier_cd)

    def test_sha_concept_path(self):
        df = self.export.concept_dimension.df
        path = df.loc[df.concept_cd == '3066e2d821aff5bf1e579fb06ea938da62caec93', 'concept_path'].values[0]
        assert path == '\\Public Studies\\TEST 17 1\\PKConc\\Timepoint Hrs.\\'

    def test_modifier_instance_num(self):
        df = self.export.observation_fact.df
        assert len(set(df[df.modifier_cd == 'TRANSMART:SAMPLE_CODE']['instance_num'])) == 2

    def test_trial_visit_dimension(self):
        df = self.export.trial_visit_dimension.df
        self.assertEqual(df.shape[0], 8)
        self.assertEqual(int(df.loc[df.rel_time_label == 'Week 6', 'rel_time_num'].values[0]), 6)
        self.assertEqual(len(self.export.observation_fact.df.trial_visit_num.unique()), 8)
        tv_num_general = df.loc[df.rel_time_label == 'General', 'trial_visit_num'].values[0]
        self.assertIn(tv_num_general, set(self.export.observation_fact.df.trial_visit_num))

    def test_non_missing_modifiers(self):
        df = self.export.observation_fact.df
        self.assertEqual((983, 24), df.shape)
        self.assertEqual(5, sum(df.modifier_cd != '@'))
        self.assertEqual(2, sum(df.tval_char == 'sample2'))
        self.assertEqual(3, sum(df.tval_char == 'sample1'))


if __name__ == '__main__':
    unittest.main()
