import os
import tmtk.utils as utils


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
        
        pass

    def validate(self):
        """
        Makes checks to determine whether transmart-batch likes this file.
        """
        pass