import os
import tmtk.utils as utils
from tmtk.utils.CPrint import CPrint


class SampleMapping(object):
    """
    Base class for subject sample mapping
    """
    def __init__(self, path=None):
        if not os.path.exists(path):
            self.path = self.create_sample_mapping(path)
        else:
            self.path = path
        self.df = utils.file2df(path)
        
        self.header = ['STUDY_ID',
                       'SITE_ID',
                       'SUBJECT_ID',
                       'SAMPLE_CD',
                       'PLATFORM',
                       'SAMPLE_TYPE',
                       'TISSUE_TYPE',
                       'TIME_POINT',
                       'CATEGORY_CD',
                       'SOURCE_CD',
                       ]

    @staticmethod
    def create_sample_mapping(path=None):
        """
        Creates a new sample mapping file and returns the location it has been given.
        """
        header = ['STUDY_ID',
                  'SITE_ID',
                  'SUBJECT_ID',
                  'SAMPLE_CD',
                  'PLATFORM',
                  'SAMPLE_TYPE',
                  'TISSUE_TYPE',
                  'TIME_POINT',
                  'CATEGORY_CD',
                  'SOURCE_CD',
                  ]
        pass

    def __str__(self):
        return self.path

    def validate(self, verbosity=2):
        """
        Makes checks to determine whether transmart-batch likes this file.
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
            return str(platform_ids[0])

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
