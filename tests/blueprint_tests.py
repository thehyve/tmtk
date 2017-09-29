import tmtk
import unittest


class BlueprintTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study()
        cls.study.Clinical.add_datafile('./studies/blueprinted/datafile.tsv')
        cls.study.apply_blueprint('./studies/blueprinted/blueprint.json')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_df_shapes(self):
        self.assertEqual(self.study.Tags.df.shape, (1, 4))
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (2, 4))
        self.assertEqual(self.study.Clinical.ColumnMapping.df.shape, (3, 7))

    def test_apply_force_categorical(self):
        self.assertEqual(sum(self.study.Clinical.ColumnMapping.df['Concept Type'] == "CATEGORICAL"), 1)

    def test_var_min_max(self):
        var = self.study.Clinical.get_variable(('datafile.tsv', 1))
        self.assertEqual(var.min, 57.468)
        self.assertEqual(var.max, 263.671)


if __name__ == '__main__':
    unittest.main()
