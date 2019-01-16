import os

import pandas as pd

from tests.commons import TestBase
from tmtk.study import Study
from tmtk.toolbox.template_reader.create_study_from_templates import COMMENT, get_template_sheets, template_reader
from tmtk.toolbox.template_reader.sheet_exceptions import ValueSubstitutionError, MetaDataException
from tmtk.toolbox.template_reader.sheets import (TreeSheet, ModifierSheet, TrialVisitSheet, BlueprintFile,
                                                 ValueSubstitutionSheet, OntologyMappingSheet)
from tmtk.utils.mappings import Mappings


class TemplateReaderTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        template_dir = os.path.join(cls.studies_dir, 'template_reader')
        cls.template_file = os.path.join(template_dir, 'Clinical_data_2017_mock_study_V2.xlsx')
        cls.template = pd.ExcelFile(cls.template_file)
        cls.incorrect_template = pd.ExcelFile(os.path.join(template_dir, 'Clinical_data_2017_mock_study_errors.xlsx'))
        cls.study = Study()

    def test_get_template_sheets(self):
        sheet_dict = get_template_sheets(self.template)
        self.assertIsInstance(sheet_dict['tree structure'], TreeSheet)
        self.assertIsInstance(sheet_dict['modifier'], ModifierSheet)
        self.assertIsInstance(sheet_dict['value substitution'], ValueSubstitutionSheet)
        self.assertIsInstance(sheet_dict['trial visit'], TrialVisitSheet)

    def test_tree_sheet(self):
        tree_sheet = TreeSheet(self.template.parse('Tree structure', comment=COMMENT))
        self.assertListEqual(tree_sheet.data_sources,
                             ['Low-dimensional data (Mock)', 'SAMPLE (Mock)', 'TRIAL_VISIT_Data (Mock)',
                              'csv_data_file.csv', 'just_another_excel_file.xlsx'])
        self.assertTupleEqual(tree_sheet.df.shape, (29, 13))
        l_ = [l for l in tree_sheet.get_meta_columns_iter()]
        mt_l = [('Level 4 metadata tag', 'Level 4 metadata value'), ('Level 5 metadata tag', 'Level 5 metadata value')]
        self.assertListEqual(l_, mt_l)
        tags_df = tree_sheet.create_metadata_tags_file()
        self.assertTupleEqual(tags_df.shape, (10, 4))
        self.assertListEqual(tags_df.columns.tolist(), Mappings.tags_header)

    def test_meta_tags_fail(self):
        tree_sheet = TreeSheet(self.template.parse('Tree structure', comment=COMMENT).iloc[:, :-1])
        self.assertRaises(MetaDataException, tree_sheet.create_metadata_tags_file)

    def test_modifier_sheet(self):
        modifier_sheet = ModifierSheet(self.template.parse('Modifier', comment=COMMENT))
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
        value_substitution_sheet = ValueSubstitutionSheet(self.template.parse('Value substitution', comment=COMMENT))
        self.assertTupleEqual(value_substitution_sheet.df.shape, (8, 4))
        key_set = {('Gender', 'Low-dimensional data (Mock)'), ('QLQ-C30_Q01', 'TRIAL_VISIT_Data (Mock)'),
                   ('QLQ-C30_Q02', 'TRIAL_VISIT_Data (Mock)'), ('QLQ-C30_Q03', 'TRIAL_VISIT_Data (Mock)'),
                   ('QLQ-C30_Q04', 'TRIAL_VISIT_Data (Mock)'), ('FAVORITE_COLOR', 'csv_data_file'),
                   ('Favorite_drill', 'just_another_excel_file')}
        self.assertSequenceEqual(value_substitution_sheet.word_map.keys(), key_set)

    def test_trial_visit_sheet(self):
        trial_visit_sheet = TrialVisitSheet(self.template.parse('Trial visit', comment=COMMENT))
        self.assertTupleEqual(trial_visit_sheet.df.shape, (7, 3))
        self.assertListEqual(trial_visit_sheet.df.columns.tolist(), Mappings.trial_visits_header)

    def test_ontology_mapping_sheet(self):
        s = OntologyMappingSheet(self.template.parse('Ontology mapping', comment=COMMENT))
        self.assertEqual((2, 4), s.df.shape)

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
        tree_sheet = TreeSheet(self.template.parse('Tree structure', comment=COMMENT))
        b = BlueprintFile(tree_sheet)
        self.assertIn(('Blood_Volume', 'SAMPLE (Mock)'), b.blueprint)
        self.assertEqual(len(b.blueprint), 32)
        self.assertDictEqual(
            {
                'label': 'Blood volume',
                'path': '3. Biobank\\Blood'
            },
            b.blueprint[('Blood_Volume', 'SAMPLE (Mock)')]
        )

        update_item = {('Blood_Volume', 'SAMPLE (Mock)'):
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
            b.blueprint[('Blood_Volume', 'SAMPLE (Mock)')]
        )

        new_item = {'RESERVED_KEYWORD':
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
            }, b.blueprint['RESERVED_KEYWORD']
        )

    def test_template_reader(self):
        study = template_reader(self.template_file)
        col_map = study.Clinical.ColumnMapping.df
        modifiers = study.Clinical.Modifiers.df
        self.assertTupleEqual(col_map.shape, (44, 7))

        used_modifiers = col_map.iloc[:, -1].unique().tolist()
        [self.assertIn(item, modifiers.modifier_cd.unique().tolist()+[''])
         for item in used_modifiers]

    def test_clinical_sources_in_study(self):
        study = template_reader(self.template_file)
        clinical_sources_in_study = {var.filename for var in study.Clinical.all_variables.values()}
        self.assertEqual(clinical_sources_in_study, {'Low-dimensional data (Mock).txt',
                                                     'SAMPLE (Mock).txt',
                                                     'TRIAL_VISIT_Data (Mock).txt',
                                                     'just_another_excel_file.txt',
                                                     'csv_data_file.txt'
                                                     })

    def test_data_labels_in_study(self):
        study = template_reader(self.template_file)
        expected = {'1. Trouble strenuous activities',
                    '2. Trouble long walk',
                    '3. Trouble short walk',
                    '4. Stay in bed or chair',
                    'Abnormality',
                    'Age',
                    'Blood volume',
                    'CEA (blood/serum)',
                    'Cause of death',
                    'Cause of life',
                    'Date resection primary tumor',
                    'Drill of choice',
                    'Favorite color',
                    'Gender',
                    'History of colon polyps',
                    'Hypermutated',
                    'LDH (serum)',
                    'Lesion diameter',
                    'Localization biopsy',
                    'Location primary tumor',
                    'M stage',
                    'MODIFIER',
                    'OMIT',
                    'Overall survival after resection primary tumor',
                    'Overall survival: event',
                    'Previous adjuvant therapy',
                    'Radiotherapy primary tumor',
                    'START_DATE',
                    'SUBJ_ID',
                    'Sequence colonoscopy',
                    'Subject identifiers',
                    'T stage',
                    'TRIAL_VISIT_LABEL'
                    }

        found = {var.data_label for var in study.Clinical.all_variables.values()}
        self.assertEqual(expected, found)

    def test_word_map_in_study(self):
        study = template_reader(self.template_file)
        var_wm_d = {var_key.tuple: var.word_map_dict for var_key, var in study.Clinical.all_variables.items()
                    if var.is_in_wordmap}
        # Reduce wordmap dicts to only k-v pairs that are not identical and not nan
        var_wm_d = {var: {k: v for k, v in wm.items() if k != v and not pd.isnull(k)} for var, wm in var_wm_d.items()}
        expected = {('Low-dimensional data (Mock).txt', 3): {'F': 'Female', 'M': 'Male'},
                    ('TRIAL_VISIT_Data (Mock).txt', 4): {'1': '1. Not at all'},
                    ('TRIAL_VISIT_Data (Mock).txt', 5): {'2': '2. A little'},
                    ('TRIAL_VISIT_Data (Mock).txt', 6): {'3': '3. Quite a bit'},
                    ('TRIAL_VISIT_Data (Mock).txt', 7): {'4': '4. Very much'},
                    ('csv_data_file.txt', 2): {'Blue': 'No, yellow!'},
                    ('just_another_excel_file.txt', 3): {'Wood': 'Plastic'}
                    }
        self.assertEqual(expected, var_wm_d)
