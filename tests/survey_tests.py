import unittest
import tmtk
import pandas as pd
from io import StringIO
from contextlib import redirect_stdout


class ValidationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/survey/study.params')
        cls.export = tmtk.toolbox.SkinnyExport(cls.study)
        cls.export.build_observation_fact()

    @classmethod
    def tearDownClass(cls):
        pass

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

    def test_get_dimensions(self):
        self.assertIn('Missing Value', self.study.get_dimensions())


if __name__ == '__main__':
    unittest.main()
