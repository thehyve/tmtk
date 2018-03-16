from contextlib import redirect_stdout

import pandas as pd
from io import StringIO

from tmtk.utils import validate
from tests.commons import TestBase, create_study_from_dir


class ValidationTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('valid_study')
        cls.invalid_study = create_study_from_dir('invalid_study')

    def test_cnv_params_loading(self):
        self.assertEqual(self.study.Params.cnv.datatype, 'cnv')

    def test_cnv_params_validation(self):
        self.assertTrue(self.study.Params.cnv.validate())

    def test_cnv_highdim_load(self):
        self.assertEqual(type(self.study.HighDim.cnv.df), pd.DataFrame)

    def test_cnv_highdim_validation(self):
        self.assertTrue(self.study.HighDim.cnv.validate())

    def test_proteomics_params_loading(self):
        self.assertEqual(self.study.Params.proteomics.datatype, 'proteomics')

    def test_proteomics_params_validation(self):
        self.assertTrue(self.study.Params.proteomics.validate())

    def test_proteomics_highdim_load(self):
        self.assertEqual(type(self.study.HighDim.proteomics.df), pd.DataFrame)

    def test_proteomics_highdim_validation(self):
        self.assertTrue(self.study.HighDim.proteomics.validate())

    def test_clinical_params_loading(self):
        self.assertEqual(self.study.Params.clinical.datatype, 'clinical')

    def test_clinical_params_validation(self):
        self.assertTrue(self.study.Params.clinical.validate())

    def test_rnaseq_params_loading(self):
        self.assertEqual(self.study.Params.rnaseq.datatype, 'rnaseq')

    def test_rnaseq_params_validation(self):
        self.assertTrue(self.study.Params.rnaseq.validate())

    def test_rnaseq_highdim_load(self):
        self.assertEqual(type(self.study.HighDim.rnaseq.df), pd.DataFrame)

    def test_rnaseq_highdim_validation(self):
        self.assertTrue(self.study.HighDim.rnaseq.validate())

    def test_annotation_params_loading(self):
        self.assertEqual(self.study.Params.mrna_annotation_GPL570_bogus_annotation.datatype, 'mrna_annotation')

    def test_annotation_params_validation(self):
        self.assertTrue(self.study.Params.mrna_annotation_GPL570_bogus_annotation.validate())

    def test_annotation_platform_detections(self):
        self.assertEqual(self.study.Annotations.mrna_GPL570_BOGUS.platform, 'GPL570_BOGUS')

    def test_annotation_load(self):
        self.assertEqual(type(self.study.Annotations.mrna_GPL570_BOGUS.df), pd.DataFrame)

    def test_validate_all(self):
        self.assertTrue(self.study.validate_all())

    def test_tags_validation(self):
        self.assertTrue(self.study.Tags.validate())

    def test_invalid_word_map(self):
        error_template = '>> \033[95m[ERROR] {}\033[0m'
        warning_template = '>> \033[93m[WARNING] {}\033[0m'

        with StringIO() as buffer, redirect_stdout(buffer):
            self.invalid_study.Clinical.validate(validate.WARNING)
            messages = [line.strip("'") for line in buffer.getvalue().splitlines() if line != '']

        self.assertEqual(len(messages), 4, "Messages length is {} instead of 4".format(len(messages)))
        missing_file_error = "The file {} isn't included in the column map".format('Not_present_file.txt')
        self.assertEqual(messages[1], error_template.format(missing_file_error))

        column_index_error = "File {} doesn't has {} columns, but {} columns".format('Cell-line_clinical.txt', 10, 9)
        self.assertEqual(messages[2], error_template.format(column_index_error))

        unmapped_warning = "Value {} is mapped at column {} in file {}. " \
                           "However the value is not present in the column".format("Not_present", 8,
                                                                                   'Cell-line_clinical.txt')
        self.assertEqual(messages[3], warning_template.format(unmapped_warning))

    def test_cnv_probs(self):
        self.assertFalse(self.invalid_study.HighDim.cnv._validate_probabilities())

    def test_expression_header(self):
        self.assertFalse(self.invalid_study.HighDim.expression._validate_id_ref())



