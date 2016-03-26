"""tmtk - A toolkit for ETL curation for the tranSMART data warehouse."""
import glob
import os
import sys
import pandas as pd

__version__ = '0.1.0'
__author__ = 'Jochem Bijlard <j.bijlard@gmail.com>'
__all__ = []


class Bunch(object):
  def __init__(self, adict):
    self.__dict__.update(adict)


class Study(object):
    """
    Describes an entire TranSMART study in ETL.
    """
    def __init__(self, params_path=None):
        if os.path.basename(params_path) != 'study.params':
            print('Please give a path to study.params file.')
        else:
            self.params_path = params_path
            self._create_params_list()

    def _create_params_list(self):
        study_folder = os.path.dirname(self.params_path)
        print("Searching '{}' for *.params files.".format(study_folder))
        os.chdir(study_folder)
        self.params_file = {}
        for f in glob.iglob('*/**/*.params', recursive=True):
            print("Found {}".format(f))
            data_type = os.path.basename(f).split('.params')[0]
            split_path = f.split('/')
            subdir = '_'.join(split_path[:-1])
            subdir = subdir.replace(' ', '_')
            self.__dict__[subdir] = ParamsFile(params_path=f, data_type=data_type)


class ParamsFile(object):
    """
    Class for parameter files
    """
    def __init__(self, params_path="", data_type=""):
        self.path = params_path
        self.data_type = data_type
        self.parameters = {}
        with open(self.path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if '=' in line and line[0] != '#':
                    param = line.split('=')
                    self.parameters[param[0]] = param[1]


if __name__ == '__main__':
    print('This is not meant to run directly.')
    sys.exit(1)