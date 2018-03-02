import unittest

import pandas as pd

from tmtk.study import Study
from tmtk.toolbox.template_reader.create_study_from_templates import COMMENT, EXPECTED_SHEETS, get_template_sheets, \
    template_reader
from tmtk.toolbox.template_reader.sheet_exceptions import ValueSubstitutionError, MetaDataException, TemplateException
from tmtk.toolbox.template_reader.sheets import TreeSheet, ModifierSheet, TrialVisitSheet, BlueprintFile, \
    ValueSubstitutionSheet
from tmtk.utils.mappings import Mappings


class TemplateReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_file = 'studies/template_reader/Clinical_data_2017_mock_study_V2.xlsx'
        cls.template = pd.ExcelFile(cls.template_file)
        cls.incorrect_template = pd.ExcelFile('studies/template_reader/Clinical_data_2017_mock_study_errors.xlsx')
        cls.study = Study()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_template_sheets(self):
        t, m, vs, tv = get_template_sheets(self.template)
        self.assertIsInstance(t, TreeSheet)
        self.assertIsInstance(m, ModifierSheet)
        self.assertIsInstance(vs, ValueSubstitutionSheet)
        self.assertIsInstance(tv, TrialVisitSheet)

    def test_get_template_sheets_error(self):
        self.assertRaises(TemplateException, get_template_sheets, self.incorrect_template)

    def test_tree_sheet(self):
        tree_sheet = TreeSheet(self.template.parse(EXPECTED_SHEETS['TreeSheet'], comment=COMMENT))
        self.assertListEqual(tree_sheet.data_sources,
                             ['Low-dimensional data (Mock)', 'SAMPLE (Mock)', 'TRIAL_VISIT_Data (Mock)'])
        self.assertTupleEqual(tree_sheet.df.shape, (25, 12))
        l_ = [l for l in tree_sheet.get_meta_columns_iter()]
        mt_l = [('Level 4 metadata tag', 'Level 4 metadata value'), ('Level 5 metadata tag', 'Level 5 metadata value')]
        self.assertListEqual(l_, mt_l)
        tags_df = tree_sheet.create_metadata_tags_file()
        self.assertTupleEqual(tags_df.shape, (7, 4))
        self.assertListEqual(tags_df.columns.tolist(), Mappings.tags_header)

    def test_meta_tags_fail(self):
        tree_sheet = TreeSheet(self.template.parse(EXPECTED_SHEETS['TreeSheet'], comment=COMMENT).iloc[:, :-1])
        self.assertRaises(MetaDataException, tree_sheet.create_metadata_tags_file)

    def test_modifier_sheet(self):
        modifier_sheet = ModifierSheet(self.template.parse(EXPECTED_SHEETS['ModifierSheet'], comment=COMMENT))
        self.assertTupleEqual(modifier_sheet.df.shape, (3, 4))
        self.assertDictEqual(modifier_sheet.modifier_blueprint, {})

        modifier_sheet.set_initial_modifier_blueprint(self.study.Clinical.Modifiers.df)
        self.assertIn('SAMPLE_ID', modifier_sheet.modifier_blueprint)

        modifier_sheet.update_modifier_blueprint('Blood@UNIT')
        self.assertIn('Blood@UNIT', modifier_sheet.modifier_blueprint)
        reference_column = 'Blood'
        data_type = 'UNIT'
        self.assertDictEqual(modifier_sheet.modifier_blueprint['Blood@UNIT'], {'label': 'MODIFIER',
                                                                               'data_type': data_type,
                                                                               'reference_column': reference_column})

    def test_value_substitution_sheet(self):
        value_substitution_sheet = ValueSubstitutionSheet(
            self.template.parse(EXPECTED_SHEETS['ValueSubstitutionSheet'], comment=COMMENT))
        self.assertTupleEqual(value_substitution_sheet.df.shape, (6, 4))
        key_set = {'Gender', 'QLQ-C30_Q01', 'QLQ-C30_Q02', 'QLQ-C30_Q03', 'QLQ-C30_Q04'}
        self.assertSequenceEqual(value_substitution_sheet.word_map.keys(), key_set)

    def test_trial_visit_sheet(self):
        trial_visit_sheet = TrialVisitSheet(self.template.parse(EXPECTED_SHEETS['TrialVisitSheet'], comment=COMMENT))
        self.assertTupleEqual(trial_visit_sheet.df.shape, (7, 3))
        self.assertListEqual(trial_visit_sheet.df.columns.tolist(), Mappings.trial_visits_header)

    def test_trial_visit_sheet_exception(self):
        value_df = pd.DataFrame.from_dict({
            'column name': {
                0: 'QLQ-C30_Q04',
                1: 'QLQ-C30_Q04'},
            'from value': {
                0: '4',
                1: '4'},
            'sheet name/file name': {
                0: 'TRIAL_VISIT_Data (Mock)',
                1: 'TRIAL_VISIT_Data (Mock)'},
            'to value': {
                0: '4. Very much',
                1: '4. Test_wrong'}
        })
        self.assertRaises(ValueSubstitutionError, ValueSubstitutionSheet, value_df)

    def test_blue_print_file(self):
        tree_sheet = TreeSheet(self.template.parse(EXPECTED_SHEETS['TreeSheet'], comment=COMMENT))
        b = BlueprintFile(tree_sheet)
        self.assertIn('Blood_Volume', b.blueprint)
        self.assertEqual(len(b.blueprint), 29)
        self.assertDictEqual(
            {
                'label': 'Blood volume',
                'path': '3. Biobank\\Blood'
            },
            b.blueprint['Blood_Volume']
        )

        update_item = {'Blood_Volume':
            {
                'label': 'Volume of blood',
                'path': '3. Biobank',
                'new_item': 'test'
            }
        }
        b.update_blueprint_item(update_item)
        self.assertDictEqual(
            {
                'label': 'Volume of blood',
                'path': '3. Biobank',
                'new_item': 'test'
            },
            b.blueprint['Blood_Volume']
        )

        new_item = {'test_item':
            {
                'label': 'this is a test',
                'path': 'some path',
            }
        }

        b.update_blueprint(new_item)
        self.assertDictEqual(
            {
                'label': 'this is a test',
                'path': 'some path',
            }, b.blueprint['test_item']
        )

    def test_template_reader(self):
        study = template_reader(self.template_file)
        col_map = study.Clinical.ColumnMapping.df
        modifiers = study.Clinical.Modifiers.df
        self.assertTupleEqual(col_map.shape, (39,7))

        used_modifiers = col_map.iloc[:,-1].unique().tolist()
        [self.assertIn(item, modifiers.modifier_cd.unique().tolist()+[''])
         for item in used_modifiers]


