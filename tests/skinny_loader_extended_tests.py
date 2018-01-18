import tmtk
import tempfile
import unittest
import shutil


class SkinnyLoaderExtendedTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/survey/study.params')
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        pass

    def test_no_top_node(self):
        self.export = tmtk.toolbox.SkinnyExport(self.study, self.temp_dir, add_top_node=False)
        self.assertEqual((19, 27), self.export.i2b2_secure.df.shape)


if __name__ == '__main__':
    unittest.main()
