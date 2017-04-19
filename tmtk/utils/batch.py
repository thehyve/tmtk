from tmtk.utils.Generic import clean_for_namespace

import os
from glob import glob
from pathlib import Path
import subprocess
import socket
import re

from threading import Thread
import tqdm
import ipywidgets
from IPython.display import display

from ._batch_job_descriptions import JobStepsDescription, job_map

import logging
logger = logging.getLogger('tmtk')
logger.setLevel(level=logging.INFO)


class JobProperties:
    def __init__(self, path, tmbatch=None, param=None, items_expected=None):
        self.path = path
        self.filename = os.path.basename(path)
        self.tmbatch = tmbatch
        self.param = param
        self.items_expected = items_expected

        # To be set from property file
        self.driver = None
        self.url = None
        self.user = None
        self.password = None

        with open(path, 'r') as f:
            for line in f.readlines():
                key, value = line.strip().split('=', 1)
                setattr(self, key.split('batch.jdbc.', 1)[1], value)

    def __repr__(self):
        return 'Add "()" to call transmart-batch with property file: {!r}'.format(self.filename)

    def _repr_html_(self):
        return 'Add "()" to call transmarte: {!r}'.format(self.filename)

    def __call__(self, *args, **kwargs):
        if self.check_connection():
            return self.tmbatch.run_job(properties_file=self.path, *args, **kwargs)

    def _valid(self):
        return all([self.driver, self.url, self.user, self.password])

    def is_postgres(self):
        return 'postgresql' in self.url

    @property
    def host(self):
        if self.is_postgres():
            return re.findall('//([^:]+):', self.url)[0]
        else:
            return re.findall('@([^:]+):', self.url)[0]

    @property
    def port(self):
        return int(re.findall(self.host + ':([0-9]+)', self.url)[0])

    def check_connection(self):
        s = socket.socket()
        try:
            s.connect((self.host, self.port))
            return True
        except Exception as e:
            print("something's wrong with {}:{}. Exception is {}".format(self.host, self.port, e))
            return False
        finally:
            s.close()


class Destinations:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TransmartBatch:

    def __init__(self, param=None, items_expected=None):
        self._items_expected = items_expected
        self._param = param

    @property
    def tmbatch_home(self):
        """Path of the TMBATCH_HOME environment variable."""
        home = os.environ.get('TMBATCH_HOME')
        if not home:
            raise EnvironmentError('Environment variable $TMBATCH_HOME not set.')
        return home

    def run_job(self, properties_file, param=None, log=True, silent=None, items_expected=None):
        """
        Run an actual transmart-batch job.

        :param properties_file:
        :param param:
        :param log:
        :param silent:
        :param items_expected:
        :return:
        """

        param = param or self._param
        items_expected = items_expected or self._items_expected

        job_type = os.path.basename(param)
        if log and type(log) != str:
            log = os.path.join(os.path.dirname(param), 'transmart-batch.log')

        if job_type == 'study.params':
            f_or_p = '-f'
            param = os.path.dirname(param)
        else:
            f_or_p = '-p'

        job = [self.batch_jar, '-c', properties_file, '-n', f_or_p, param]
        logger.warning("Starting job: {}".format(" ".join([s.replace(self.tmbatch_home, '$TMBATCH_HOME') for s in job])))

        job = BatchJob(job, job_type=job_type, log=log, silent=silent, items_expected=items_expected)
        job.start()
        return job

    @property
    def batch_jar(self):
        jars = [str(p) for p in Path(self.tmbatch_home).glob('**/*transmart*batch*.jar')]
        if not jars:
            raise Exception("No transmart-batch .jar file found in $TMBATCH_HOME.")

        if len(jars) > 1:
            logger.warning("Multiple transmart-batch .jar files found in $TMBATCH_HOME, using youngest.")

        youngest = jars[0]
        for jar in jars[1:]:
            if os.path.getmtime(youngest) < os.path.getmtime(jar):
                youngest = jar
        return youngest

    def _get_property_files(self, *args, **kwargs):
        """
        Dictionary of all property files.

        :return: dictionary of TransmartBatchProperties objects.
        """
        files = [JobProperties(p, tmbatch=self, *args, **kwargs) for p in glob(os.path.join(self.tmbatch_home, "*.properties"))]
        return {clean_for_namespace(p.filename.rsplit('.properties', 1)[0]): p for p in files}

    def get_loading_namespace(self, *args, **kwargs):
        """
        Return a namespace object with different destination to load data to.

        :param param: parameter file to be used in transmart-batch command.
        :return: Destinations namespace.
        """
        return Destinations(**self._get_property_files(*args, **kwargs))


class BatchJob(Thread):

    def __init__(self, job=None, items_expected=None, job_type=None, log=None, silent=None):
        self.job = job
        self._silent = silent
        self.process = None
        self.job_type = job_type
        self.log = log
        self._items_expected = items_expected
        super().__init__()

    def run(self):

        self.process = subprocess.Popen(self.job,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True)

        if not self._silent:
            JobLogger(stdout_stream=self.process.stdout,
                      log=self.log,
                      items_expected=self._items_expected)


class JobLogger:

    _all_jobs_tell = 'o.t.b.startup.RunJob - Following params'
    _new_job_tell = 'o.t.b.startup.RunJob - Start processing'
    _step_tell = 'o.s.b.c.j.SimpleStepHandler - Executing step:'
    _items_written_tell = 'o.t.b.b.ProgressWriteListener - Items written:'

    _div = '<div style="margin-top:4px;">{}</div>'
    _html_status = _div.format('<b>Step ({i_step}/{n_step}):</b> {desc} ({step_name})')
    _status = 'Step ({i_step}/{n_step}): {desc} ({step_name})'
    _status_total = 'Job {i_job} out of {n_job}. Currently running: {cur_job!r}'
    _html_status_total = _div.format('Job {i_job} out of {n_job}. Currently running: {cur_job!r}')
    _html_status_initial = _div.format('Job {i_job} out of {n_job}. Currently running: {cur_job!r}')

    _bar_format       = 'Job:    | {bar} | {desc}'
    _bar_format_total = 'Total:  | {bar} | {desc}'

    def __init__(self, stdout_stream, log=None, items_expected=None):

        self._items_expected = items_expected
        self.log = log or os.devnull

        if type(items_expected) == dict:
            self._multi_job = True
            self._all_jobs_items_n = sum(items_expected.values())
        else:
            self._multi_job = False
            self._all_jobs_items_n = None

        self._all_jobs = None
        self._all_jobs_n = None
        self._all_jobs_items_i = 0
        self.current_job = None
        self.params_found = None
        self._job_description = None
        self.current_step = None
        self._items_current_step = 0
        self._status_override = None
        self._last_warning = None

        self._widget_shown = False
        display(self)

        self.start_log(stdout_stream)

    def _repr_html_(self):

        self._html_progress_total = ipywidgets.IntProgress(max=self._all_jobs_items_n)
        self._html_widget_total = ipywidgets.HTML(value=self._html_status_initial)
        self._html_box_total = ipywidgets.HBox([self._html_progress_total, self._html_widget_total])

        self._html_progress = ipywidgets.IntProgress()
        self._html_widget = ipywidgets.HTML(value=self._html_status_initial)
        self._html_box = ipywidgets.HBox([self._html_progress, self._html_widget])

        if self._multi_job:
            self._html_output = ipywidgets.VBox([self._html_box_total, self._html_box])
        else:
            self._html_output = self._html_box

        if not self._widget_shown:
            self._widget_shown = True
            display(self._html_output)

        return ' '

    def __repr__(self):
        return ' '

    def update_progress(self):
        if self._widget_shown:
            self._html_widget.value = self._html_status.format(
                step_name=self.current_step or '*',
                i_step=self.job_step_i,
                n_step=self.job_step_n,
                desc=self.job_step_description)
            self._html_progress.value = self._items_current_step or 0

            self._html_widget_total.value = self._html_status_total.format(
                i_job=self._job_i,
                n_job=self._all_jobs_n,
                cur_job=self.params_found
            )
            self._html_progress_total.value = self._all_jobs_items_i + self._html_progress.value

            self._status_override = None
        else:
            try:
                self._progress.set_description(self._status.format(
                    step_name=self.current_step or '*',
                    i_step=self.job_step_i,
                    n_step=self.job_step_n,
                    desc=self.job_step_description
                ))
                self._progress.n = self._items_current_step or 0
                self._progress.update()

                self._progress_total.set_description(self._status_total.format(
                    i_job=self._job_i,
                    n_job=self._all_jobs_n,
                    cur_job=self.params_found
                ))
                self._progress_total.n = self._all_jobs_items_i + self._progress.n
                self._progress_total.update()

                self._status_override = None
            except AttributeError as e:
                print(e)
                self._load_tqdm()

    def _load_tqdm(self):
        self._progress_total = tqdm.tqdm(bar_format=self._bar_format_total, initial=0,
                                         desc='Launching, please wait..',
                                         total=self._all_jobs_items_n)

        self._progress = tqdm.tqdm(bar_format=self._bar_format, initial=0, total=10,
                                   desc='Launching, please wait..')


    @property
    def items_expected(self):
        try:
            return self._items_expected.get(self.current_job, 0)
        except AttributeError:
            return self._items_expected

    @property
    def _job_i(self):
        try:
            return self._all_jobs.index(self.current_job) + 1
        except ValueError:
            return '*'

    @property
    def job_step_i(self):
        try:
            return self.job_description.position_of(self.current_step) or 0
        except AttributeError:
            return '*'

    @property
    def job_step_n(self):
        try:
            return self.job_description.n_steps
        except AttributeError:
            return '*'

    @property
    def job_step_description(self):
        try:
            return self._status_override or self.job_description.description_of(self.current_step)
        except AttributeError:
            return '*'

    @property
    def job_description(self):
        return self._job_description

    @job_description.setter
    def job_description(self, value):
        self._job_description = value
        # Reset progress bar
        try:
            self._html_progress.max = self.items_expected
        except AttributeError:
            self._progress.close()
            del self._progress
            self._progress = tqdm.tqdm(bar_format=self._bar_format,
                                       initial=0,
                                       total=self.items_expected,
                                       desc='Launching, please wait..')
        self._items_current_step = 0

    def start_log(self, stdout_stream):
        with open(self.log, 'a') as f:
            for line in stdout_stream:
                f.write(line)
                self._row_parser(line)

    def _row_parser(self, line):
        if '[WARN]' in line[:100]:
            self._last_warning = line

        if self._all_jobs_tell in line[:140]:
            self._all_jobs = [j.rsplit(', ', 1)[-1]+'.params' for j in line.strip(']) \n').split('.params')]
            try:
                self._all_jobs.remove('.params')
            except ValueError:
                pass
            self._all_jobs_n = len(self._all_jobs)

        elif self._new_job_tell in line[:140]:
            # Add items of previous job to all jobs total
            self._all_jobs_items_i += self.items_expected

            # Set the new job from output
            self.current_job = line.split('.params')[0].rsplit(', ', 1)[1] + '.params'

            # Set job description
            self.params_found = self.current_job.rsplit(os.sep, 1)[1]
            self.job_description = job_map.get(self.params_found)
            self._status_override = 'Job registered for {}'.format(self.params_found)

        elif self._step_tell in line[:140]:
            self.current_step = line.rsplit('[', 1)[1].strip('[] \n')

        elif self._items_written_tell in line[:140] and self.current_step == self.job_description.progress_bar_step:
            items_written = line.split('o.t.b.b.ProgressWriteListener - Items written: ')[1].split(',')[0]
            self._items_current_step = int(items_written)
            self._status_override = 'loading data items.. {} items written.'.format(items_written)

        elif line.endswith('[COMPLETED]\n'):
            self._items_current_step = self.items_expected
            self._status_override = 'Job complete.'
            logger.info("Job complete: {}".format(self.current_job))

        elif line.endswith('[UNKNOWN]\n') or line.endswith('[FAILED]\n'):
            self._status_override = 'Job failed.'
            logger.warning("Job failed: {}".format(self.current_job))
            logger.warning("With error: {}".format(self._last_warning))
            if self.log:
                print("See log for more info: {}".format(self.log))

        else:
            return

        self.update_progress()
