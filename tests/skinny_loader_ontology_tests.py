import tmtk

from tests.commons import TestBase, create_study_from_dir


class SkinnyOntologyTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('TEST_ONTOLOGY')
        cls.export = tmtk.toolbox.SkinnyExport(cls.study, cls.temp_dir)
        cls.export.build_observation_fact()

    def test_multiple_parents(self):
        df = self.export.i2b2_secure.df
        assert '\\Demographics\\' in df['c_fullname'].values
        assert '\\Demographics\\Gender\\' in df['c_fullname'].values
        assert '\\Demographics\\Race\\' in df['c_fullname'].values
        assert '\\Heritage\\' in df['c_fullname'].values
        assert '\\Heritage\\Race\\' in df['c_fullname'].values

    def test_not_used(self):
        df = self.export.i2b2_secure.df
        assert '\\Demographics\\Not used\\' not in df['c_fullname'].values
