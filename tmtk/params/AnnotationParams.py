from tmtk.params import ParamsBase
import tmtk.utils as utils
import os


class AnnotationParams(ParamsBase):

    @property
    def mandatory(self):
        return ['PLATFORM', 'TITLE', 'ANNOTATIONS_FILE']

    @property
    def optional(self):
        return ['ORGANISM', 'GENOME_RELEASE']

    def is_viable(self):
        """

        :return: True if both the platform is set and the annotations file is located,
        else returns False.
        """
        if self.__dict__.get('ANNOTATIONS_FILE', None) and self.__dict__.get('PLATFORM', None):
            file_found = os.path.exists(os.path.join(self.dirname, self.ANNOTATIONS_FILE))
            return file_found
        else:
            return False
