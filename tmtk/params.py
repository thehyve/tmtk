import os
import tmtk.utils as utils
import glob


class Params:
    """
    Container class for all params files, called by Study to locate all params files.
    """
    def __init__(self, study_folder=None):
        """
        :param study_folder: points to a study.params file at the root of a study.
        """
        assert os.path.exists(study_folder), 'Params: {} does not exist.'.format(study_folder)

        for f in glob.iglob(os.path.join(study_folder, '*/**/*.params'), recursive=True):
            datatype = os.path.basename(f).split('.params')[0]
            if 'kettle' in str(f):  # Skip subdirectories that have kettle in the name.
                continue

            relative_path = f.split(study_folder)[1]
            subdir = self._pick_subdir_name(relative_path, datatype)
            self.__dict__[subdir] = ParamsFile(path=f, datatype=datatype, subdir=subdir)

    @staticmethod
    def _pick_subdir_name(relative_path, datatype):
        """
        Private function that finds a suitable subdir name.
        :param relative_path:
        :param datatype:
        :return:
        """
        split_path = relative_path.strip('/').split('/')
        subdir = '_'.join(split_path[:-1])
        subdir = utils.clean_for_namespace(subdir)
        if not subdir.startswith(datatype):
            subdir = "{}_{}".format(datatype, subdir)
        return subdir


class ParamsFile:
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
        if parameters == None:
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
                    self.__dict__[param] = value
        if subdir:
            self.subdir = subdir
        else:
            self.subdir = self.path

    def __str__(self):
        return self.subdir

    def validate(self, verbosity=2):
        """
        Validate this parameter file.
        :param verbosity:
        :return:
        """
        if self.datatype == 'clinical':
            message = self._validate_clinical()

        elif 'annotation' in self.datatype:
            message = self._validate_annotations()

        elif self.datatype == 'tags':
            message = self._validate_tags()

        elif self.datatype in ['acgh', 'rnaseq', 'expression', 'proteomics']:
            message = self._validate_hd()

        else:
            message = ['({}) Not implemented in transmart-batch, skipping..'.format(self.datatype)]

        if message:
            heading = '\nValidating {}'.format(self.path)
            utils.print_message_list(message, head=heading)

    def _validate_clinical(self):
        mandatory = ['COLUMN_MAP_FILE',
                     ]
        optional = ['WORD_MAP_FILE',
                    'XTRIAL_FILE',
                    'TAGS_FILE',
                    ]

        return self._check_for_correct_params(mandatory, optional)

    def _validate_annotations(self):
        mandatory = ['PLATFORM',
                     'TITLE',
                     'ANNOTATIONS_FILE'
                     ]
        optional = ['ORGANISM',
                    'GENOME_RELEASE'
                    ]

        return self._check_for_correct_params(mandatory, optional)

    def _validate_tags(self):
        mandatory = ['TAGS_FILE',
                     ]
        optional = [
                    ]

        return self._check_for_correct_params(mandatory, optional)

    def _validate_hd(self):
        mandatory = ['DATA_FILE',
                     'DATA_TYPE',
                     'MAP_FILENAME',
                     ]
        optional = ['LOG_BASE',
                    'ALLOW_MISSING_ANNOTATIONS'
                    ]

        return self._check_for_correct_params(mandatory, optional)

    def _check_for_correct_params(self, mandatory, optional):
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
