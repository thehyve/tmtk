import tmtk
import tempfile
import pandas as pd
import unittest


class BlueprintTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study()
        cls.study.Clinical.add_datafile('./studies/blueprinted_modifier/datafile.tsv')
        cls.modifiers = pd.read_csv('./studies/blueprinted_modifier/modifiers.txt', sep='\t')
        cls.modifiers.set_index('modifier_cd',drop=False,inplace=True)
        cls.study.Clinical.Modifiers.df = cls.modifiers
        cls.study.study_id = 'test'
        cls.study.top_node = '\\Public Studies\\Test\\'
        cls.study.apply_blueprint('./studies/blueprinted_modifier/blueprint.json')
        cls.temp_dir = tempfile.mkdtemp()
        cls.export = tmtk.toolbox.SkinnyExport(cls.study, cls.temp_dir)
        cls.export.build_observation_fact()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_df_shapes(self):
        self.assertEqual(self.study.Tags.df.shape, (1, 4))
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (2, 4))
        self.assertEqual(self.study.Clinical.ColumnMapping.df.shape, (4, 7))

    def test_apply_force_categorical(self):
        self.assertEqual(sum(self.study.Clinical.ColumnMapping.df['Data Type'] == "CATEGORICAL"), 1)


    def test_modifier_added(self):
        self.assertEqual(sum(self.study.Clinical.ColumnMapping.df['Data Type'] == "TEST_MOD"), 1)

    def test_non_missing_modifiers(self):
        df = self.export.observation_fact.df
        pat = self.export.patient_dimension.df[['patient_num','sourcesystem_cd']].merge(
            df, how='left', on='patient_num')
        self.assertEqual((24, 24), df.shape)
        self.assertEqual(12, sum(df.modifier_cd != '@'))
        self.assertEqual(2, sum(df.tval_char == 'RANDOM6'))
        self.assertEqual(8, sum(pat.sourcesystem_cd_x == 'SUBJECT4'))

    def test_var_min_max(self):
        var = self.study.Clinical.get_variable(('datafile.tsv', 1))
        self.assertEqual(var.min, 57.468)
        self.assertEqual(var.max, 280.0)

    def test_underscore_plus(self):
        assert '\\Demographics\\_information\\+other' in self.study.Clinical.ColumnMapping.df['Category Code'][1]
        # json_data = self.study.concept_tree_json
        # assert 'Demographics_information+other' in json_data
    #     json_data = json_data.replace('_information', '_info+_mation')
    #     tmtk.arborist.update_study_from_json(self.study, json_data)
    #     assert '\\Demographics\\_info\\+\\_mation\\+other' in self.study.Clinical.ColumnMapping.df['Category Code'][1]


if __name__ == '__main__':
    unittest.main()
