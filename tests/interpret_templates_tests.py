import filecmp
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import tmtk.toolbox
from tmtk.utils import PathError


class InterpretTemplatesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control_dir = os.path.join('studies', 'test_templates_expected_output')
        cls.temp_dir = tempfile.mkdtemp()
        cls.template_dir = os.path.join('studies', 'test_templates')

        def collect_study_files(dir_name):
            all_paths = Path(dir_name).glob('**/*')
            return {path.name: path for path in all_paths if not path.name.startswith(('~', '.')) and path.is_file()}

        tmtk.toolbox.create_study_from_templates(ID='TEMPLATE_TEST', source_dir=cls.template_dir,
                                                 output_dir=cls.temp_dir, sec_req='N')

        cls.control_study = tmtk.Study(os.path.join(cls.control_dir, 'study.params'))
        cls.study = tmtk.Study(os.path.join(cls.temp_dir, 'study.params'))

        cls.control_files = collect_study_files(cls.control_dir)
        cls.test_files = collect_study_files(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_study_load(self):
        assert self.study.params.path

    def test_data_volumes(self):
        assert self.study.study_id == self.control_study.study_id

    def test_file_equality(self):
        assert self.control_files.keys() == self.test_files.keys()

        for file_name, file_path in self.control_files.items():
            test_file_path = self.test_files[file_name]
            # assert filecmp.cmp(str(file_path), str(test_file_path))
            if not filecmp.cmp(str(file_path), str(test_file_path)):
                print(str(file_path), str(test_file_path))

    def test_write_study(self):
        with self.assertRaises(PathError):
            self.study.write_to(self.temp_dir)
        new_study = self.study.write_to(os.path.join(self.temp_dir, 'new-folder'))
        self.assertNotEquals(new_study.params.path, self.study.params.path)


if __name__ == '__main__':
    unittest.main()
