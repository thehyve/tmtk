import os
import tmtk
import unittest
import tempfile
import shutil
import re


class ValidationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/valid_study/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_acgh_params_loading(self):
        assert self.study.Params.acgh.datatype == 'acgh'

    def test_acgh_params_validation(self):

        pass

    def test_create_new_folder(self):
        pass

    def test_create_clinical_params(self):
        pass

    def test_column_map_open_and_save(self):
        pass

if __name__ == '__main__':
    unittest.main()