import tmtk
import unittest
from tmtk.utils.batch import _wrapper
import os
import io
import re


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = tmtk.Study('studies/valid_study/study.params')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    @staticmethod
    def get_log_to_stream():
        with open('./tests/batch_fop_log', 'r') as f:
            tmp_log = f.read()

        tmtk_path = os.path.abspath(os.path.realpath(os.getcwd()))
        for _path in re.findall(r'( /home/vlad-the-impaler/.*?\.params)', tmp_log):
            # replace path in log with local path
            new_path = _path.replace('/home/vlad-the-impaler/tmtk', tmtk_path)
            new_path = new_path.replace('/', os.sep)

            # adapt tmp_log to reflect local machine
            tmp_log = tmp_log.replace(_path, new_path)

        return io.StringIO(tmp_log)

    def test_file_length(self):
        assert _wrapper.file_length(self.study.Clinical.Cell_line_clinical_txt.path) == 19

    def test_job_logger(self):
        log = _wrapper.StatusParser(stdout_stream=self.get_log_to_stream(), non_html=True, log=False, silent=True,
                                    items_expected=self.study._study_total_batch_items)

        # Some checks to determine the job ran well
        assert log.all_jobs_items_n == 284
        assert log.all_jobs_items_trunc == 282
        assert log.items_current_step == 2
        assert log.current_step == 'tagsLoadStep'

    def test_job_logger_console(self):
        log = _wrapper.StatusParser(stdout_stream=self.get_log_to_stream(), non_html=True, log=False,
                                    items_expected=self.study._study_total_batch_items)

        # Some checks to determine the job ran well
        assert log.all_jobs_items_n == 284
        assert log.all_jobs_items_trunc == 282
        assert log.items_current_step == 2
        assert log.current_step == 'tagsLoadStep'

    def test_job_logger_javascript(self):
        log = _wrapper.StatusParser(stdout_stream=self.get_log_to_stream(), log=False,
                                    items_expected=self.study._study_total_batch_items)

        # Some checks to determine the job ran well
        assert log.all_jobs_items_n == 284
        assert log.all_jobs_items_trunc == 282
        assert log.items_current_step == 2
        assert log.current_step == 'tagsLoadStep'


if __name__ == '__main__':
    unittest.main()
