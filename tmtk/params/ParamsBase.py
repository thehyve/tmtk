import os
import tmtk.utils as utils
from tmtk.utils.CPrint import MessageCollector

class ParamsBase:
    """
    Base class for parameter files.
    """
    def __init__(self, path=None, datatype=None, parameters=None, subdir=None, parent=None):
        """
        :param path: describes the path to the params file.
        :param datatype: the parameters belong to.
        :param parameters: is a dictionary that contains all parameters in the file.
        :param subdir: is the key that is given by Study class.
        :param parent: can be used to find the parent instance of this object.
        """
        if not parameters:
            parameters = {}
        self.path = path
        self.dirname = os.path.dirname(path)
        self.datatype = datatype
        self._parent = parent
        with open(self.path, 'r') as f:
            for line in f.readlines():
                # Only keep things before a comment character
                line = line.strip().split('#', 1)[0]
                if '=' in line:
                    parameter = line.split('=')
                    param = parameter[0]
                    value = parameter[1].strip("\'\"")
                    if param == 'PLATFORM':
                        value = value.upper()
                    if param == 'DATA_FILE_PREFIX':
                        param = 'DATA_FILE'
                    self.__dict__[param] = value
        if subdir:
            self.subdir = subdir
        else:
            self.subdir = self.path

    def __str__(self):
        return self.subdir

    def _check_for_correct_params(self, mandatory, optional, messages):
        """

        :param mandatory:
        :param optional:
        :return:
        """
        for param in mandatory:
            value = self.__dict__.get(param, None)
            if not value:
                messages.error('No {} given.'.format(param))

        for param, value in self.__dict__.items():
            if param.islower():
                continue
            messages.info('Detected parameter {}={}.'.format(param, value))
            if param not in mandatory + optional:
                messages.error('Illegal param found: {}.'.format(param))
            elif 'FILE' in param:
                if not os.path.exists(os.path.join(self.dirname, value)):
                    messages.error('{}={} cannot be found.'.format(param, value))
                else:
                    messages.okay('{}={} found.'.format(param, value))

    def validate(self, verbosity=2):
        """
        Validate this parameter file. Return True if no errors were found in this parameter file.
        :param verbosity:
        :return: True or False.
        """
        messages = MessageCollector(verbosity=verbosity)

        messages.head("Validating params file at {}".format(self))
        self._check_for_correct_params(self.mandatory, self.optional, messages=messages)

        messages.flush()
        return not messages.found_error
