import os
import pandas as pd

import tmtk
from tests.commons import TestBase


class BlueprintModifierTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = tmtk.Study()
        dir_ = os.path.join(cls.studies_dir, 'blueprinted_modifier')
        cls.study.Clinical.add_datafile(os.path.join(dir_, 'datafile.tsv'))
        cls.modifiers = pd.read_csv(os.path.join(dir_, 'modifiers.txt'), sep='\t')
        cls.modifiers.set_index('modifier_cd', drop=False, inplace=True)
        cls.study.Clinical.Modifiers.df = cls.modifiers
        cls.study.study_id = 'test'
        cls.study.top_node = '\\Public Studies\\Test\\'
        cls.study.apply_blueprint(os.path.join(cls.studies_dir, 'blueprinted_modifier', 'blueprint.json'))
        cls.export = tmtk.toolbox.SkinnyExport(cls.study, cls.temp_dir)
        cls.export.build_observation_fact()

    def test_df_shapes(self):
        self.assertEqual(self.study.Tags.df.shape, (1, 4))
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (2, 4))
        self.assertEqual(self.study.Clinical.ColumnMapping.df.shape, (5, 7))

    def test_apply_force_categorical(self):
        self.assertEqual(sum(self.study.Clinical.ColumnMapping.df['Data Type'] == "CATEGORICAL"), 1)

    def test_modifier_added(self):
        self.assertEqual(sum(self.study.Clinical.ColumnMapping.df['Data Type'] == "TEST_MOD"), 1)

    def test_non_missing_modifiers(self):
        df = self.export.observation_fact.df
        pat = self.export.patient_dimension.df[['patient_num', 'sourcesystem_cd']].merge(
            df, how='left', on='patient_num')
        self.assertEqual((30, 24), df.shape)
        self.assertEqual(18, sum(df.modifier_cd != '@'))
        self.assertEqual(2, sum(df.tval_char == 'RANDOM6'))
        self.assertEqual(10, sum(pat.sourcesystem_cd_x == 'SUBJECT4'))

    def test_var_min_max(self):
        var = self.study.Clinical.get_variable(('datafile.tsv', 1))
        self.assertEqual(var.min, 57.468)
        self.assertEqual(var.max, 280.0)

    def test_blueprint_reference_column(self):
        bpbase = self.study.Clinical.find_variables_by_label("Blood pressure (baseline)")[0]
        self.assertEqual(2, len(bpbase.modifiers))
        gender = self.study.Clinical.find_variables_by_label("Gender")[0]
        self.assertEqual(1, len(gender.modifiers))
        self.assertEqual(1, self.study.Clinical.ColumnMapping.df.iloc[4, 4])
