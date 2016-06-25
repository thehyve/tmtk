import tmtk
import os
import unittest
import tempfile
import shutil
import re
import pandas as pd


class IncompletenessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/incomplete/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_study_load(self):
        assert self.study.params_path

    def test_empty_wordmap(self):
        assert self.study.Clinical.WordMapping.validate(0)

    def test_non_existing_wordmap(self):
        self.study.Params.clinical.WORD_MAP_FILE = 'fake_wordmap.txt'
        assert self.study.Clinical.WordMapping.validate(0)
        self.study.Params.clinical.WORD_MAP_FILE = 'Cell-line_wordmap.txt'

    def test_create_json_string(self):
        assert tmtk.arborist.create_concept_tree(self.study)

if __name__ == '__main__':
    unittest.main()
