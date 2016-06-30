import os
from ..utils import PathError
from ..utils.CPrint import MessageCollector


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

        self.path = path
        self.dirname = os.path.dirname(path)
        self.datatype = datatype
        self._parent = parent
        if not parameters:
            self.__dict__.update(**self._get_params_from_file())
        else:
            self.__dict__.update(**parameters)

        if subdir:
            self.subdir = subdir
        else:
            self.subdir = self.path

    def __str__(self):
        return self.subdir

    def __repr__(self):
        return self.path

    def _get_params_from_file(self):
        """

        :param path:
        :return: dictionary with all variables in file
        """
        params_dict = {}
        with open(self.path, 'r') as f:
            for line in f.readlines():
                # Only keep things before a comment character
                line = line.split('#', 1)[0]
                line = line.strip()
                if '=' not in line:
                    continue
                parameter = line.split('=')
                param = parameter[0]
                value = parameter[1].strip("\'\"")
                if param == 'PLATFORM':
                    value = value.upper()
                if param == 'DATA_FILE_PREFIX':
                    param = 'DATA_FILE'
                params_dict[param] = value
        return params_dict

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
            if param not in mandatory and param not in optional:
                messages.error('Illegal param found: {}.'.format(param))
            elif 'FILE' in param:
                if not os.path.exists(os.path.join(self.dirname, value)):
                    messages.error('{}={} cannot be found.'.format(param, value))
                else:
                    messages.okay('{}={} found.'.format(param, value))

    def validate(self, verbosity=3):
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

    def write_to(self, path, overwrite=False):
        """
        Writes parameter file to path.
        """

        def _write_dict(f, d):
            for param, d in d.items():
                value = self.__dict__.get(param)
                if value:
                    row = '# {}\n{}={}\n'.format(d.get('helptext'), param, value)
                    f.write(row)

        if not path:
            raise PathError(path)

        if not overwrite and os.path.exists(path):
            raise PathError("{} already exists. Consider setting `overwrite=True`".format(self.path))

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w') as f:
            f.write('### Mandatory\n')
            _write_dict(f, self.mandatory)
            f.write('\n### Optional\n')
            _write_dict(f, self.optional)

    def save(self):
        """
        Overwrite the original file with the current parameters.
        """
        self.write_to(self.path, overwrite=True)
