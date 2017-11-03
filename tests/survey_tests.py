import tmtk
import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd


class SurveyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/survey/study.params')
        cls.temp_dir = tempfile.mkdtemp()
        cls.export = tmtk.toolbox.SkinnyExport(cls.study, cls.temp_dir)
        cls.export.build_observation_fact()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        pass

    def test_column_map_shape(self):
        assert self.study.Clinical.ColumnMapping.df.shape == (9, 7)

    def test_observation_count(self):
        assert self.export.observation_fact.df.shape == (13, 24)

    def test_modifier_type(self):
        var = self.study.Clinical.get_variable(('survey_data.tsv', 9))
        self.assertEqual(var.modifier_code, 'MISSVAL')
        self.assertEqual(var.column_type, 'CATEGORICAL')
        self.assertEqual(var.data_label, 'MODIFIER')
        self.assertIn('Missing Value', self.export.dimension_description.df.name.values)

    def test_modifier_observations(self):
        obs_df = self.export.observation_fact.df
        values = list(obs_df.loc[obs_df.concept_cd == 'description', 'tval_char'])
        self.assertIn(pd.np.nan, values)
        self.assertIn('Not Specified', values)
        self.assertIn('Bradwurst', values)

    def test_get_dimensions(self):
        self.assertIn('Missing Value', self.study.get_dimensions())

    def test_back_populate_ontology(self):
        i2b2_df = self.export.i2b2_secure.df

        self.assertEqual(i2b2_df.shape, (21, 27))
        self.assertIn('\\Ontology\\Demographics\\', set(i2b2_df.c_fullname))
        self.assertEqual(i2b2_df.loc[i2b2_df.c_fullname == '\\Ontology\\Demographics\\', 'secure_obj_token'].values[0],
                         'PUBLIC')
        self.assertEqual(
            i2b2_df.loc[i2b2_df.c_fullname == '\\Projects\\Survey 1\\Interests\\', 'secure_obj_token'].values[0],
            'SURVEY'
        )

    def test_visualattributes(self):
        vis_attrs = {'CA', 'FA', 'FAS', 'LAC', 'LAD', 'LAN', 'LAT'}
        found = set(self.export.i2b2_secure.df.c_visualattributes)
        for it in vis_attrs:
            self.assertIn(it, found)
        for it in found:
            self.assertIn(it, vis_attrs)

    def test_to_disk(self):
        self.export.to_disk()

        p = Path(self.temp_dir)
        self.assertIn('i2b2demodata', [f.name for f in p.glob('i2b2*')])
        self.assertIn('i2b2metadata', [f.name for f in p.glob('i2b2*')])
        self.assertEqual(len([f for f in p.glob('*/*tsv')]), 11)


if __name__ == '__main__':
    unittest.main()
