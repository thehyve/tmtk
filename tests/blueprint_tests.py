import os

import tmtk
from tests.commons import TestBase


class BlueprintTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = tmtk.Study()
        dir_ = os.path.join(cls.studies_dir, 'blueprinted')
        cls.study.Clinical.add_datafile(os.path.join(dir_, 'datafile.tsv'))
        cls.study.apply_blueprint(os.path.join(dir_, 'blueprint.json'))

    def test_df_shapes(self):
        self.assertEqual(self.study.Tags.df.shape, (1, 4))
        self.assertEqual(self.study.Clinical.WordMapping.df.shape, (2, 4))
        self.assertEqual(self.study.Clinical.ColumnMapping.df.shape, (3, 7))

    def test_apply_force_categorical(self):
        self.assertEqual(sum(self.study.Clinical.ColumnMapping.df['Data Type'] == "CATEGORICAL"), 1)

    def test_var_min_max(self):
        var = self.study.Clinical.get_variable(('datafile.tsv', 1))
        self.assertEqual(var.min, 57.468)
        self.assertEqual(var.max, 263.671)

    def test_underscore_plus(self):
        self.assertIn('\\Demographics\\_information\\+other',
                      self.study.Clinical.ColumnMapping.df['Category Code'][1])
        json_data = self.study.concept_tree_json
        self.assertIn('Demographics_information+other', json_data)
        json_data = json_data.replace('_information', '_info+_mation')
        tmtk.arborist.update_study_from_json(self.study, json_data)
        self.assertIn('\\Demographics\\_info\\+\\_mation\\+other',
                      self.study.Clinical.ColumnMapping.df['Category Code'][1])
