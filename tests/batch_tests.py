import io
import os
import re
from tests.commons import TestBase, create_study_from_dir
from tmtk.utils.batch import _wrapper, __main__ as main
from tmtk import options

properties_file = """\
batch.jdbc.driver=org.postgresql.Driver
batch.jdbc.url=jdbc:postgresql://localhost:5434/transmart
batch.jdbc.user=tm_cz
batch.jdbc.password=tm_cz
"""


class BatchTests(TestBase):
    
    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('valid_study')
        cls.tmp_batch_home = os.path.join(cls.temp_dir, 'batch_home')
        os.makedirs(cls.tmp_batch_home)

        cls.properties_file = os.path.join(cls.tmp_batch_home, 'batchdb.properties')
        cls.fake_jar = os.path.join(cls.tmp_batch_home, 'transmart-batch-fake.jar')
        with open(cls.properties_file, 'w') as writer:
            writer.write(properties_file)
        with open(cls.fake_jar, 'w') as writer:
            writer.write('')

    @staticmethod
    def get_log_to_stream():
        log_file = os.path.join(os.path.dirname(__file__), 'batch_fop_log')
        with open(log_file, 'r') as f:
            tmp_log = f.read()

        tmtk_path = os.path.abspath(os.path.realpath(os.getcwd().rstrip('\\/tes')))
        for _path in re.findall(r'( /home/vlad-the-impaler/.*?\.params)', tmp_log):
            # replace path in log with local path
            new_path = _path.replace('/home/vlad-the-impaler/tmtk', tmtk_path)
            new_path = new_path.replace('/', os.sep)

            # adapt tmp_log to reflect local machine
            tmp_log = tmp_log.replace(_path, new_path)

        return io.StringIO(tmp_log)

    def test_file_length(self):
        self.assertEqual(_wrapper.file_length(self.study.Clinical.Cell_line_clinical_txt.path), 19)

    def test_job_logger(self):
        log = _wrapper.StatusParser(stdout_stream=self.get_log_to_stream(), non_html=True, log=False, silent=True,
                                    items_expected=self.study._study_total_batch_items)

        # Some checks to determine the job ran well
        self.assertEqual(log.all_jobs_items_n, 284)
        self.assertEqual(log.all_jobs_items_trunc, 282)
        self.assertEqual(log.items_current_step, 2)
        self.assertEqual(log.current_step, 'tagsLoadStep')

    def test_job_logger_console(self):
        log = _wrapper.StatusParser(stdout_stream=self.get_log_to_stream(), non_html=True, log=False,
                                    items_expected=self.study._study_total_batch_items)

        # Some checks to determine the job ran well
        self.assertEqual(log.all_jobs_items_n, 284)
        self.assertEqual(log.all_jobs_items_trunc, 282)
        self.assertEqual(log.items_current_step, 2)
        self.assertEqual(log.current_step, 'tagsLoadStep')

    def test_job_logger_javascript(self):
        log = _wrapper.StatusParser(stdout_stream=self.get_log_to_stream(), log=False,
                                    items_expected=self.study._study_total_batch_items)

        # Some checks to determine the job ran well
        self.assertEqual(log.all_jobs_items_n, 284)
        self.assertEqual(log.all_jobs_items_trunc, 282)
        self.assertEqual(log.items_current_step, 2)
        self.assertEqual(log.current_step, 'tagsLoadStep')

    def test_cli_help(self):
        with self.assertRaises(SystemExit):
            main.run_batch(['--help'])

    def test_cli_list(self):
        with self.assertRaises(SystemExit):
            main.run_batch(['--list'])

    def test_properties(self):
        options.transmart_batch_home = self.tmp_batch_home
        self.assertEqual(1, len(self.study.load_to.__dict__.keys()))

    def test_run(self):
        options.transmart_batch_home = self.tmp_batch_home
        items_expected = self.study._study_total_batch_items
        executable = _wrapper.TransmartBatch(self.study.params.path, items_expected)
        self.assertEqual(executable.tmbatch_home, self.tmp_batch_home)
        self.assertEqual(executable.batch_jar, self.fake_jar)
        executable.run_job(properties_file=self.properties_file)
