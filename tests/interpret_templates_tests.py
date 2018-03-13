import os
from pathlib import Path

import tmtk.toolbox
from tmtk.utils import PathError

from tests.commons import TestBase


def compare_two_files(file1, file2):
    with open(str(file1), 'r') as reader1:
        with open(str(file2)) as reader2:
            reader1 = reader1.readlines()
            reader2 = reader2.readlines()

            if len(reader1) != len(reader2):
                return False

            for i in range(len(reader1)):
                if reader1[i].strip() != reader2[i].strip():
                    return False

    return True


class InterpretTemplatesTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.control_dir = os.path.join(cls.studies_dir, 'test_templates_expected_output')
        cls.template_dir = os.path.join(cls.studies_dir, 'test_templates')

        def collect_study_files(dir_name):
            all_paths = Path(dir_name).glob('**/*')
            return {path.name: path for path in all_paths if not path.name.startswith(('~', '.')) and path.is_file()}

        tmtk.toolbox.create_study_from_templates(ID='TEMPLATE_TEST', source_dir=cls.template_dir,
                                                 output_dir=cls.temp_dir, sec_req='N')

        cls.control_study = tmtk.Study(os.path.join(cls.control_dir, 'study.params'))
        cls.study = tmtk.Study(os.path.join(cls.temp_dir, 'study.params'))

        cls.control_files = collect_study_files(cls.control_dir)
        cls.test_files = collect_study_files(cls.temp_dir)

    def test_study_load(self):
        self.assertTrue(os.path.exists(self.study.params.path))

    def test_data_volumes(self):
        self.assertEqual(self.study.study_id, self.control_study.study_id)

    def test_file_equality(self):
        self.assertEqual(self.control_files.keys(), self.test_files.keys())

        for file_name, file_path in self.control_files.items():
            test_file_path = self.test_files[file_name]
            self.assertTrue(compare_two_files(str(file_path), str(test_file_path)))

    def test_write_study(self):
        with self.assertRaises(PathError):
            self.study.write_to(self.temp_dir)
        new_study = self.study.write_to(os.path.join(self.temp_dir, 'new-folder'))
        self.assertNotEqual(new_study.params.path, self.study.params.path)
