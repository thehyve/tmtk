import tmtk
import os
import unittest
import tempfile
import shutil
import re
import pandas as pd


class ArboristTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/valid_study/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_study_load(self):
        assert self.study.params_path == 'studies/valid_study/study.params'

    def test_create_json_string(self):
        assert tmtk.arborist.create_concept_tree(self.study)

if __name__ == '__main__':
    unittest.main()
