import tmtk
import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd


class SkinnyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/TEST_17_1/study.params')
        cls.temp_dir = tempfile.mkdtemp()
        cls.export = tmtk.toolbox.SkinnyExport(cls.study, cls.temp_dir)
        cls.export.build_observation_fact()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        pass

    # def test_column_map_shape(self):
    # This test refers to the wrong study
    #     assert self.study.Clinical.ColumnMapping.df.shape == (9, 7)

    def test_update_instance_num(self):
        export_df = self.export.observation_fact.df[self.export.observation_fact.primary_key]
        assert export_df.duplicated().sum() == 0

    def test_row_wide_modifiers(self):
        # Requires test study to be extended with modifiers
        # TODO: Extend TEST_17_1 with modifiers with empty reference column (so row wide)
        assert 'a' == 'a'

    def test_sha_concept_path(self):
        # Need to extract simple path from the study to compare the SHA1 for
        assert 'a' == 'a'


if __name__ == '__main__':
    unittest.main()
