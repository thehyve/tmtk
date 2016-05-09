from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class StudyParams(ParamsBase):

    @property
    def mandatory(self):
        return ['STUDY_ID']

    @property
    def optional(self):
        return ['SECURITY_REQUIRED', 'TOP_NODE']

    def is_viable(self):
        """

        :return: True if STUDY_ID has been set.
        """
        if self.__dict__.get('STUDY_ID', None):
            return True
        else:
            return False
