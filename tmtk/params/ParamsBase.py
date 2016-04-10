import os
import tmtk.utils as utils


class ParamsBase:
    """
    Class for parameter files.
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

    def _check_for_correct_params(self, mandatory, optional):
        """

        :param mandatory:
        :param optional:
        :return:
        """
        messages = []
        for param in mandatory:
            value = self.__dict__.get(param, None)
            if not value:
                messages.append('No {} given.'.format(param))

        for param, value in self.__dict__.items():
            if param.islower():
                continue
            if param not in mandatory + optional:
                messages.append('Disallowed param found: {}.'.format(param))
            elif 'FILE' in param and not os.path.exists(
                    os.path.join(self.dirname, value)):
                messages.append('{}={} cannot be found.'.format(param, value))
        return messages

    def _process_validation_message(self, message=None):
        """

        :param message:
        :return:
        """
        if message:
            heading = '\nValidating {}'.format(self.path)
            utils.print_message_list(message, head=heading)
            return False
        else:
            return True
