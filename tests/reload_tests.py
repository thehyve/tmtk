import tmtk
import unittest


class ReloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.study = tmtk.Study('studies/incomplete/study.params')

    def test_change_study_id(self):
        assert self.study.study_id == 'CLUC'
        self.study.study_id = 'NEW_CLUC_ID'
        assert self.study.study_id == 'NEW_CLUC_ID'
        assert self.study.HighDim.rnaseq.sample_mapping.study_id == 'NEW_CLUC_ID'

    def test_change_study_name(self):
        assert self.study.study_name == 'CLUC'
        assert not self.study.params.get('TOP_NODE')
        self.study.study_name = 'Cell lines'
        assert self.study.params.get('TOP_NODE') == '\\Private Studies\\Cell lines'


if __name__ == '__main__':
    unittest.main()
