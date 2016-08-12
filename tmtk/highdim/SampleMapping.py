import os

from ..utils import CPrint, FileBase, md5, path_converter


class SampleMapping(FileBase):
    """
    Base class for subject sample mapping
    """

    def __init__(self, path=None):
        if not os.path.exists(path):
            self.path = self.create_sample_mapping(path)
        else:
            self.path = path
        super().__init__()

    @property
    def get_concept_paths(self):
        """
        Get all concept paths from file, replaces ATTR1 and ATTR2.

        :return: dictionary with md5 hash values as key and paths as value
        """
        paths = self.df.apply(self._find_path, axis=1)
        return {md5(p): p for p in paths}

    @staticmethod
    def _find_path(row):
        cp = row.ix[8]
        cp = cp.replace('ATTR1', str(row.ix[6]))
        cp = cp.replace('ATTR2', str(row.ix[7]))

        return path_converter(cp)

    def update_concept_paths(self, path_dict):
        self.df.ix[:, 8] = self.df.apply(lambda x: self._update_row(x, path_dict), axis=1)

    def _update_row(self, row, path_dict):
        current_path = self._find_path(row)
        current_md5 = md5(current_path)
        new_path = path_dict.get(current_md5)
        if new_path:
            return new_path
        else:
            return current_path

    def __str__(self):
        return self.path

    def validate(self, verbosity=2):
        """
        Checks whether transmart-batch likes this file.
        """
        pass

    @property
    def samples(self):
        return list(self.df.ix[:, 3])

    @property
    def platform(self):
        """
        :return: the platform id in this sample mapping file.
        """
        platform_ids = list(self.df.ix[:, 4].unique())
        if len(platform_ids) > 1:
            CPrint.warn('Found multiple platforms in {}. '
                        'This might lead to unexpected behaviour.'.format(self.path))
        elif platform_ids:
            return str(platform_ids[0]).upper()

    @property
    def study_id(self):
        """

        :return: study_id in sample mapping file
        """
        study_ids = list(self.df.ix[:, 0].unique())
        if len(study_ids) > 1:
            CPrint.error('Found multiple study_ids found in {}. '
                         'This is not supported.'.format(self.path))
        elif study_ids:
            return str(study_ids[0]).upper()
