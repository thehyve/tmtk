import tmtk
import os
import unittest
import tempfile
import shutil
import re
import pandas as pd


class RemappingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/remap/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def test_study_load(self):
        assert self.study.params_path

    # def test_create_annotation_file(self):
    #     new_anno = tmtk.Toolbox.generate_chromosomal_regions_file(platform_id='given_gpl_id',
    #                                                               reference_build='hg38',
    #                                                               only_y=True)
    #     assert new_anno.GPL_ID[1] == 'given_gpl_id'

    def test_remap_functionality(self):
        remapped = tmtk.Toolbox.remap_chromosomal_regions(
            datafile=self.study.HighDim.rnaseq.df,
            destination_platform=self.study.Annotations.acgh_ACGH_ANNOT.df,
            origin_platform=self.study.Annotations.rnaseq_RNASEQ_ANNOT.df
        )
        assert remapped.ix[0, 0] == '_WASH7P'
        assert (remapped.ix[:, 1] == [3.0, 38.5, 0.0, 1.0]).all()

    def test_remapping_shortcut(self):
        highdim_acgh = self.study.HighDim.acgh
        chrom_regions = self.study.Annotations.rnaseq_RNASEQ_ANNOT
        remapped = highdim_acgh.remap_to(destination=chrom_regions)
        assert remapped.dtypes[3] == 'int64'
        assert (remapped.ix[:, 1] == [0, 0, 0, 1, 1]).all()

    def test_df_and_object_remap_input(self):
        highdim_acgh = self.study.HighDim.acgh
        chrom_regions = self.study.Annotations.rnaseq_RNASEQ_ANNOT
        assert all(highdim_acgh.remap_to(chrom_regions) == highdim_acgh.remap_to(chrom_regions.df))

if __name__ == '__main__':
    unittest.main()
