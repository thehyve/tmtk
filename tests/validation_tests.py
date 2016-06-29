import os
import tmtk
import unittest
import tempfile
import shutil
import re
import pandas as pd


class ValidationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/valid_study/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_cnv_params_loading(self):
        assert self.study.Params.cnv.datatype == 'cnv'

    def test_cnv_params_validation(self):
        assert self.study.Params.cnv.validate(0)

    def test_cnv_highdim_load(self):
        assert type(self.study.HighDim.cnv.df) == pd.DataFrame

    def test_cnv_highdim_validation(self):
        assert self.study.HighDim.cnv.validate(0)

    def test_proteomics_params_loading(self):
        assert self.study.Params.proteomics.datatype == 'proteomics'

    def test_proteomics_params_validation(self):
        assert self.study.Params.proteomics.validate(0)

    def test_proteomics_highdim_load(self):
        assert type(self.study.HighDim.proteomics.df) == pd.DataFrame

    def test_proteomics_highdim_validation(self):
        assert self.study.HighDim.proteomics.validate(0)

    def test_clinical_params_loading(self):
        assert self.study.Params.clinical.datatype == 'clinical'

    def test_clinical_params_validation(self):
        assert self.study.Params.clinical.validate(0)

    def test_rnaseq_params_loading(self):
        assert self.study.Params.rnaseq.datatype == 'rnaseq'

    def test_rnaseq_params_validation(self):
        assert self.study.Params.rnaseq.validate(0)

    def test_rnaseq_highdim_load(self):
        assert type(self.study.HighDim.rnaseq.df) == pd.DataFrame

    def test_rnaseq_highdim_validation(self):
        assert self.study.HighDim.rnaseq.validate(0)

    def test_annotation_params_loading(self):
        assert self.study.Params.mrna_annotation_GPL570_bogus_annotation.datatype == 'mrna_annotation'

    def test_annotation_params_validation(self):
        assert self.study.Params.mrna_annotation_GPL570_bogus_annotation.validate(0)

    def test_annotation_platform_detections(self):
        assert self.study.Annotations.mrna_GPL570_BOGUS.platform == 'GPL570_BOGUS'

    def test_annotation_load(self):
        assert type(self.study.Annotations.mrna_GPL570_BOGUS.df) == pd.DataFrame

    def test_validate_all(self):
        assert not self.study.validate_all(0)

if __name__ == '__main__':
    unittest.main()