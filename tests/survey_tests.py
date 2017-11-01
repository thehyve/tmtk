import tmtk
import unittest
import tempfile
import shutil
from pathlib import Path


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

    def test_get_dimensions(self):
        self.assertIn('Missing Value', self.study.get_dimensions())

    def test_back_populate_ontology(self):
        self.assertIn('\\Ontology\\Demographics\\', set(self.export.i2b2_secure.df.c_fullname))
        self.assertEqual(self.export.i2b2_secure.df.shape, (21, 27))

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
        self.assertEqual(len([f for f in p.glob('*/*tsv')]), 10)


if __name__ == '__main__':
    unittest.main()
