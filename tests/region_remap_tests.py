import tmtk
import pandas as pd

from tests.commons import TestBase, create_study_from_dir


class RemappingTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('remap')

    def test_study_load(self):
        self.assertNotEqual(self.study.params.path, None)

    def test_remap_functionality(self):
        remapped = tmtk.toolbox.remap_chromosomal_regions(
            datafile=self.study.HighDim.rnaseq.df,
            destination_platform=self.study.Annotations.cnv_ACGH_ANNOT.df,
            origin_platform=self.study.Annotations.rnaseq_RNASEQ_ANNOT.df
        )
        self.assertEqual(remapped.iloc[0, 0], '_WASH7P')
        self.assertEqual(list(remapped.iloc[:, 1]), [3.0, 38.5, 0.0, 1.0])

    def test_remapping_shortcut(self):
        highdim_cnv = self.study.HighDim.cnv
        chrom_regions = self.study.Annotations.rnaseq_RNASEQ_ANNOT
        remapped = highdim_cnv.remap_to(destination=chrom_regions)
        self.assertEqual(remapped.dtypes[3], 'int64')
        self.assertEqual(list(remapped.iloc[:, 1]), [0, 0, 0, 1, 1])

    def test_df_and_object_remap_input(self):
        highdim_cnv = self.study.HighDim.cnv
        chrom_regions = self.study.Annotations.rnaseq_RNASEQ_ANNOT
        self.assertEqual(
            list(highdim_cnv.remap_to(chrom_regions)),
            list(highdim_cnv.remap_to(chrom_regions.df))
        )

    def test_hgnc_to_entrez(self):
        mapped = tmtk.toolbox.remap_id.hgnc_to_entrez(
            ['TP53', pd.np.nan, 'EGFR', 'ERBB2', pd.np.nan, 'definitely_not_a_gene']
        )
        self.assertEqual(len(mapped), 6)
        self.assertTrue(pd.isnull(mapped.iloc[-1]))

