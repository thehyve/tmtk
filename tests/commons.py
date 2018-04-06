import unittest

import os
import shutil
import tempfile

import tmtk


def create_study_from_dir(dir_name):
    return tmtk.Study(os.path.join(TestBase.studies_dir, dir_name, 'study.params'))


class TestBase(unittest.TestCase):

    studies_dir = os.path.join(os.path.dirname(__file__), '..', 'studies')
    temp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.setup_class_hook()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    @classmethod
    def setup_class_hook(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
