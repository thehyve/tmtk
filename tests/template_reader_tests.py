import unittest
import pandas as pd
import os

from tmtk.toolbox.template_reader.sheets import TreeSheet, ModifierSheet, TrialVisitSheet, BlueprintFile, \
    ValueSubstitutionSheet
from tmtk.toolbox.template_reader.create_study_from_templates import COMMENT, EXPECTED_SHEETS, get_template_sheets
from tmtk.utils.mappings import Mappings
from tmtk.toolbox.template_reader.sheet_exceptions import ValueSubstitutionError
from tmtk.study import Study

class TemplateReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_dir = os.path.join('studies', 'template_reader')
        cls.template = pd.ExcelFile('../studies/template_reader/Clinical_data_2017_mock_study_V2.xlsx')
        cls.study = Study()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_template_sheets(self):
        pass

    def test_tree_sheet(self):
        tree_sheet = TreeSheet(self.template.parse(EXPECTED_SHEETS['TreeSheet'], comment=COMMENT))
        assert tree_sheet.data_sources == ['Low-dimensional data (Mock)', 'SAMPLE (Mock)', 'TRIAL_VISIT_Data (Mock)']
        assert tree_sheet.df.shape == (25, 12)
        l = [l for l in tree_sheet.get_meta_columns_iter()]
        mt_l = [('Level 4 metadata tag', 'Level 4 metadata value'), ('Level 5 metadata tag', 'Level 5 metadata value')]
        assert l == mt_l
        tags_df = tree_sheet.create_metadata_tags_file()
        assert tags_df.shape == (7, 4)
        assert tags_df.columns.tolist() == Mappings.tags_header

    def test_meta_tags(self):
        pass

    def test_modifier_sheet(self):
        modifier_sheet = ModifierSheet(self.template.parse(EXPECTED_SHEETS['ModifierSheet'], comment=COMMENT))
        assert modifier_sheet.df.shape == (3,4)
        assert modifier_sheet.modifier_blueprint == {}

        modifier_sheet._set_initial_modifier_blueprint(self.study.Clinical.Modifiers.df)
        assert 'SAMPLE_ID' in modifier_sheet.modifier_blueprint

        modifier_sheet.update_modifier_blueprint('Blood@UNIT')
        assert 'Blood@UNIT' in modifier_sheet.modifier_blueprint
        reference_column = 'Blood'
        data_type= 'UNIT'
        assert modifier_sheet.modifier_blueprint['Blood@UNIT'] == {'label': 'MODIFIER',
                                                                   'data_type': data_type,
                                                                   'reference_column': reference_column}


    def test_value_substitution_sheet(self):
        value_substitution_sheet = ValueSubstitutionSheet(self.template.parse(EXPECTED_SHEETS['ValueSubstitutionSheet'], comment=COMMENT))
        assert value_substitution_sheet.df.shape == (6, 4)
        key_set = {'Gender', 'QLQ-C30_Q01', 'QLQ-C30_Q02', 'QLQ-C30_Q03', 'QLQ-C30_Q04'}
        assert set(value_substitution_sheet.word_map.keys()) == key_set

    def test_trial_visit_sheet(self):
        trial_visit_sheet = TrialVisitSheet(self.template.parse(EXPECTED_SHEETS['TrialVisitSheet'], comment=COMMENT))
        assert trial_visit_sheet.df.shape == (7, 3)
        assert trial_visit_sheet.df.columns.tolist() == Mappings.trial_visits_header

    def test_trial_visit_sheet_exception(self):
        value_df = pd.DataFrame.from_dict({
            'column name'         : {
                0: 'QLQ-C30_Q04',
                1: 'QLQ-C30_Q04'},
            'from value' : {
                0: '4',
                1: '4'},
            'sheet name/file name': {
                0: 'TRIAL_VISIT_Data (Mock)',
                1: 'TRIAL_VISIT_Data (Mock)'},
            'to value'            : {
                0: '4. Very much',
                1: '4. Test_wrong'}
        })
        self.assertRaises(ValueSubstitutionError, ValueSubstitutionSheet, value_df)

    def test_blue_print_file(self):
        pass
