import os
import glob

from ..utils import PathError, merge_two_dicts, ValidateMixin

get_input = input


class ParamsBase(ValidateMixin):
    """
    Base class for parameter files.
    """

    def __init__(self, path=None, parameters=None, subdir=None, parent=None):
        """

        :param path: describes the path to the params file.
        :param parameters: a dictionary you can provide to setup the parameter file.
        :param subdir: is the key that is given by Study class.
        :param parent: can be used to find the parent instance of this object.
        """

        self.path = path
        self.dirname = os.path.dirname(path)
        self.datatype = os.path.basename(path).split('.params')[0]
        self._parent = parent
        self.subdir = subdir

        if parameters:
            self.__dict__.update(**parameters)
        elif os.path.exists(self.path):
            self.__dict__.update(**self._params_in_file)

    def __str__(self):
        return 'Params: {} ({})'.format(self.datatype, self.path)

    def __repr__(self):
        return 'Params: {} ({})'.format(self.datatype, self.path)

    def get(self, parameter, default=None):
        """
        Return value for parameter.

        :param parameter: string will be converted to uppercase.
        :param default: return default if value is not found.
        :return: value for this parameter if set, else None.
        """
        return self.__dict__.get(parameter.upper(), default)

    def set(self, parameter, value):
        self.__dict__[parameter.upper()] = value

    @property
    def _params_in_file(self):
        """ Dictionary with all variables in file."""
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

    def write_to(self, path, overwrite=False):
        """
        Writes parameters in object to file in path. Does not
        overwrite existing files unless specifically told.

        :param path: path to store parameters to.
        :param overwrite: allow overwriting existing files.
        """

        def _write_dict(f, d):
            for param, d in d.items():
                value = self.get(param)
                if value:
                    row = '# {}\n{}={}\n'.format(d.get('helptext'), param, value)
                    f.write(row)

        if not path:
            raise PathError(path)

        if not overwrite and os.path.exists(path):
            raise PathError(
                "{} already exists. Consider setting `overwrite=True`".format(self.path))

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w') as f:
            f.write('### Mandatory\n')
            _write_dict(f, self.mandatory)
            f.write('\n### Optional\n')
            _write_dict(f, self.optional)

    def save(self):
        """Overwrite the original file with the current parameters."""
        self.write_to(self.path, overwrite=True)

    def update(self):
        """Iterate over parameters to change them interactively."""
        print('  '.join(['=' * 10, str(self) + ' params', '=' * 10]))
        for param, d in merge_two_dicts(self.mandatory, self.optional).items():
            current = self.get(param)
            default = d.get('default')
            is_file = 'FILE' in param

            print('Updating:  {}'.format(param), end='')
            if current:
                print('={}.'.format(current))
            elif default:
                print('={} (default).'.format(default))
            else:
                print(' (not set)')

            print('Helptext:  {}'.format(d.get('helptext')))

            if is_file:
                files_in_dir = [os.path.basename(f) for f in
                                glob.glob(os.path.join(self.dirname, '*')) if not os.path.isdir(f)]
                for i, f in enumerate(files_in_dir):
                    print('-    {}. {}'.format(i, f))

            new_setting = get_input('Change to:  ')

            if is_file:
                try:
                    choice = int(new_setting)
                    new_setting = files_in_dir[choice]
                except (ValueError, IndexError):
                    pass

            if new_setting and new_setting != current:
                print('Updating! ({}={})'.format(param, new_setting))
                self.__dict__[param] = new_setting

            print('-' * 20)

    def _validate_correct_params(self):
        for param in self.mandatory:
            value = self.get(param)
            if not value:
                self.msgs.error('No {} given.'.format(param))

        for param, value in self.__dict__.items():
            if param.islower():
                continue
            self.msgs.info('Detected parameter {}={}.'.format(param, value))
            if param not in self.mandatory and param not in self.optional:
                self.msgs.error('Illegal param found: {}.'.format(param))
            elif 'FILE' in param:
                if not os.path.exists(os.path.join(self.dirname, value)):
                    self.msgs.error('{}={} cannot be found on disk.'.format(param, value))
                else:
                    self.msgs.okay('{}={} found.'.format(param, value))
