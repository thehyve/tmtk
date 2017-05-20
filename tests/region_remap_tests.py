import tmtk
import unittest
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
        assert self.study.params.path

    # def test_create_annotation_file(self):
    #     new_anno = tmtk.toolbox.generate_chromosomal_regions_file(platform_id='given_gpl_id',
    #                                                               reference_build='hg38',
    #                                                               only_y=True)
    #     assert new_anno.GPL_ID[1] == 'given_gpl_id'

    def test_remap_functionality(self):
        remapped = tmtk.toolbox.remap_chromosomal_regions(
            datafile=self.study.HighDim.rnaseq.df,
            destination_platform=self.study.Annotations.cnv_ACGH_ANNOT.df,
            origin_platform=self.study.Annotations.rnaseq_RNASEQ_ANNOT.df
        )
        assert remapped.iloc[0, 0] == '_WASH7P'
        assert (remapped.iloc[:, 1] == [3.0, 38.5, 0.0, 1.0]).all()

    def test_remapping_shortcut(self):
        highdim_cnv = self.study.HighDim.cnv
        chrom_regions = self.study.Annotations.rnaseq_RNASEQ_ANNOT
        remapped = highdim_cnv.remap_to(destination=chrom_regions)
        assert remapped.dtypes[3] == 'int64'
        assert (remapped.iloc[:, 1] == [0, 0, 0, 1, 1]).all()

    def test_df_and_object_remap_input(self):
        highdim_cnv = self.study.HighDim.cnv
        chrom_regions = self.study.Annotations.rnaseq_RNASEQ_ANNOT
        assert all(highdim_cnv.remap_to(chrom_regions) == highdim_cnv.remap_to(chrom_regions.df))

    def test_hgnc_to_entrez(self):
        mapped = tmtk.toolbox.remap_id.hgnc_to_entrez(['TP53', pd.np.nan, 'EGFR', 'ERBB2', pd.np.nan, 'definitely_not_a_gene'])
        assert len(mapped) == 6
        assert pd.isnull(mapped.iloc[-1])

if __name__ == '__main__':
    unittest.main()
