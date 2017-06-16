import unittest
import tmtk
import pandas as pd
from io import StringIO
from contextlib import redirect_stdout


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/valid_study/study.params')
        cls.invalid_study = tmtk.Study('studies/invalid_study/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_cnv_params_loading(self):
        assert self.study.Params.cnv.datatype == 'cnv'

    def test_cnv_params_validation(self):
        assert self.study.Params.cnv.validate()

    def test_cnv_highdim_load(self):
        assert type(self.study.HighDim.cnv.df) == pd.DataFrame

    def test_cnv_highdim_validation(self):
        assert self.study.HighDim.cnv.validate()

    def test_proteomics_params_loading(self):
        assert self.study.Params.proteomics.datatype == 'proteomics'

    def test_proteomics_params_validation(self):
        assert self.study.Params.proteomics.validate()

    def test_proteomics_highdim_load(self):
        assert type(self.study.HighDim.proteomics.df) == pd.DataFrame

    def test_proteomics_highdim_validation(self):
        assert self.study.HighDim.proteomics.validate()

    def test_clinical_params_loading(self):
        assert self.study.Params.clinical.datatype == 'clinical'

    def test_clinical_params_validation(self):
        assert self.study.Params.clinical.validate()

    def test_rnaseq_params_loading(self):
        assert self.study.Params.rnaseq.datatype == 'rnaseq'

    def test_rnaseq_params_validation(self):
        assert self.study.Params.rnaseq.validate()

    def test_rnaseq_highdim_load(self):
        assert type(self.study.HighDim.rnaseq.df) == pd.DataFrame

    def test_rnaseq_highdim_validation(self):
        assert self.study.HighDim.rnaseq.validate()

    def test_annotation_params_loading(self):
        assert self.study.Params.mrna_annotation_GPL570_bogus_annotation.datatype == 'mrna_annotation'

    def test_annotation_params_validation(self):
        assert self.study.Params.mrna_annotation_GPL570_bogus_annotation.validate()

    def test_annotation_platform_detections(self):
        assert self.study.Annotations.mrna_GPL570_BOGUS.platform == 'GPL570_BOGUS'

    def test_annotation_load(self):
        assert type(self.study.Annotations.mrna_GPL570_BOGUS.df) == pd.DataFrame

    def test_validate_all(self):
        assert self.study.validate_all()

    def test_tags_validation(self):
        assert self.study.Tags.validate()

    def test_invalid_word_map(self):
        error_template = '\033[95m\033[91mError: {}\033[0m'
        warning_template = '\033[93mWarning: {}\033[0m'

        with StringIO() as buffer, redirect_stdout(buffer):
            self.invalid_study.Clinical.WordMapping.validate(4)
            messages = [line.strip("'") for line in buffer.getvalue().splitlines()]

        assert len(messages) == 3, "Messages length is {} instead of 4".format(len(messages))

        missing_file_error = "The file {} doesn't exists".format('Not_present_file.txt')
        assert messages[0] == error_template.format(missing_file_error), "Received {!r}".format(messages[0])

        column_index_error = "File {} doesn't has {} columns, but {} columns".format('Cell-line_clinical.txt', 10, 9)
        assert messages[1] == error_template.format(column_index_error), "Received {!r}".format(messages[1])

        unmapped_warning = "Value {} is mapped at column {} in file {}. " \
                           "However the value is not present in the column".format("Not_present", 8,
                                                                                   'Cell-line_clinical.txt')
        assert messages[2] == warning_template.format(unmapped_warning), "Received {!r}".format(messages[2])


if __name__ == '__main__':
    unittest.main()
