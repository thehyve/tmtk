import tmtk

import pandas as pd
from tests.commons import TestBase, create_study_from_dir


class SkinnyTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('TEST_17_1')
        cls.export = tmtk.toolbox.SkinnyExport(cls.study, cls.temp_dir)
        cls.export.build_observation_fact()

    def test_update_instance_num(self):
        export_df = self.export.observation_fact.df[self.export.observation_fact.primary_key]
        self.assertEqual(export_df.duplicated().sum(), 0)

    def test_row_wide_modifiers(self):
        self.assertIn('TRANSMART:SAMPLE_CODE', set(self.export.observation_fact.df.modifier_cd))

    def test_sha_concept_path(self):
        df = self.export.concept_dimension.df
        path = df.loc[df.concept_cd == '3066e2d821aff5bf1e579fb06ea938da62caec93', 'concept_path'].values[0]
        self.assertEqual(path, '\\Public Studies\\TEST 17 1\\PKConc\\Timepoint Hrs.\\')

    def test_modifier_instance_num(self):
        df = self.export.observation_fact.df
        self.assertEqual(len(set(df[df.modifier_cd == 'TRANSMART:SAMPLE_CODE']['instance_num'])), 2)

    def test_trial_visit_dimension(self):
        df = self.export.trial_visit_dimension.df
        self.assertEqual(df.shape[0], 8)
        self.assertEqual(int(df.loc[df.rel_time_label == 'Week 6', 'rel_time_num'].values[0]), 6)
        self.assertEqual(len(self.export.observation_fact.df.trial_visit_num.unique()), 8)
        tv_num_general = df.loc[df.rel_time_label == 'General', 'trial_visit_num'].values[0]
        self.assertIn(tv_num_general, set(self.export.observation_fact.df.trial_visit_num))

    def test_non_missing_modifiers(self):
        df = self.export.observation_fact.df
        self.assertEqual((989, 24), df.shape)
        self.assertEqual(5, sum(df.modifier_cd != '@'))
        self.assertEqual(2, sum(df.tval_char == 'sample2'))
        self.assertEqual(3, sum(df.tval_char == 'sample1'))

    def test_patient_dimension_nans(self):
        df = self.export.patient_dimension.df
        self.assertNotIn(pd.np.nan, set(df.sex_cd))

    def test_no_top_node(self):
        self.assertEqual((41, 27), self.export.i2b2_secure.df.shape)
        self.export2 = tmtk.toolbox.SkinnyExport(self.study, self.temp_dir, add_top_node=False)
        self.assertEqual((39, 27), self.export2.i2b2_secure.df.shape)
