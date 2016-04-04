import glob
from .utils import *
from .clinical import *


class Bunch(object):
    """
    Namespace class to allow for dot.<key> autocomplete notation.
    """
    def __init__(self, a_dict):
        self.as_dict = a_dict
        self.__dict__.update(a_dict)

    @staticmethod
    def clean_for_namespace(value):
        disallowed = ['/', '-', ' ', '.']
        for item in disallowed:
            value = value.replace(item, '_')
        return value


class Study(object):
    """
    Describes an entire TranSMART study in ETL.

    :param study_params_path: points to a study.params file at the root of a study.
    """
    def __init__(self, study_params_path=None):
        if os.path.basename(study_params_path) != 'study.params':
            print('Please give a path to study.params file.')
            raise PathError
        self.params_path = study_params_path
        self.study_folder = os.path.dirname(self.params_path)
        self.Params = Bunch(self._create_params_list())

        clinical_params = self.find_params_for_datatype(datatype='clinical')
        if len(clinical_params) == 1:
            self.Clinical = Clinical(clinical_params[0])

    def _create_params_list(self):
        """
        Private function finds all parameter files in study subdirectories.
        """
        params = {}
        for f in glob.iglob(os.path.join(self.study_folder, '*/**/*.params'), recursive=True):
            datatype = os.path.basename(f).split('.params')[0]
            subdir = self._pick_subdir_name(f, datatype)
            params[subdir] = ParamsFile(path=f, datatype=datatype)
        return params

    def _pick_subdir_name(self, abs_path, datatype):
        """
        Private function that finds a suitable subdir name.
        """
        relative_dir = abs_path.split(self.study_folder)[1]
        split_path = relative_dir.strip('/').split('/')
        subdir = '_'.join(split_path[:-1])
        subdir = Bunch.clean_for_namespace(subdir)
        if not subdir.startswith(datatype):
            subdir = "{}_{}".format(datatype, subdir)
        return subdir

    def find_params_for_datatype(self, datatype=None):
        """
        Returns a list of Params files for specific datatype in this study.
        """
        params_list = []
        for key, params_object in self.Params.as_dict.items():
            if params_object.datatype == datatype:
                params_list.append(params_object)
        return params_list

    def __str__(self):
        n_data_assets = len(self.Params)
        statement = "Study object with {} data assets.".format(n_data_assets)
        return statement

    def validate_all(self):
        pass


class ParamsFile:
    """
    Class for parameter files.

    :param path describes the path to the params file.
    :param datatype the parameters belong to.
    :param parameters is a dictionary that contains all parameters in the file.
    """
    def __init__(self, path=None, datatype=None, parameters=None):
        if parameters == None:
            parameters = {}
        self.path = path
        self.dirname = os.path.dirname(path)
        self.datatype = datatype
        with open(self.path, 'r') as f:
            for line in f.readlines():
                line = line.strip().split('#', 1)[0]
                if '=' in line:
                    param = line.split('=')
                    self.__dict__[param[0]] = param[1]

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass

    def __str__(self):
        statement = 'String representation for ParamsFile not implemented yet.'
        return statement

    def validate(self):
        pass