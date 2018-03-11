import os

from tests.commons import TestBase, create_study_from_dir


class ReloadTests(TestBase):
    """
    Tests where study is reloaded for every test.
    """

    def setUp(self):
        self.study = create_study_from_dir('incomplete')

    def test_change_study_id(self):
        self.assertEqual(self.study.study_id, 'CLUC')
        self.study.study_id = 'NEW_CLUC_ID'
        self.assertEqual(self.study.study_id, 'NEW_CLUC_ID')
        self.assertEqual(self.study.HighDim.rnaseq.sample_mapping.study_id, 'NEW_CLUC_ID')

    def test_change_study_name(self):
        self.assertEqual(self.study.study_name, 'CLUC')
        self.assertEqual(self.study.params.get('TOP_NODE'), None)
        self.study.study_name = 'Cell lines'
        self.assertEqual(self.study.params.get('TOP_NODE'), '\\Private Studies\\Cell lines')
        self.study.security_required = False
        self.assertEqual(self.study.top_node, '\\Public Studies\\Cell lines')

    def test_write_study(self):
        self.study.write_to(os.path.join(self.temp_dir, 'test_write'))
        self.assertTrue(
            os.path.exists(
                os.path.join(self.temp_dir, 'test_write', 'study.params')
            )
        )
