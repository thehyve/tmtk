import os
import tmtk.utils as utils
import tmtk


class AnnotationBase(object):
    """
    Base class for annotation files.

    :param path: path to annotation file.
    """
    def __init__(self, params=None, path=None):
        if hasattr(params, 'ANNOTATIONS_FILE'):
            self.path = os.path.join(params.dirname, params.ANNOTATIONS_FILE)
            self.platform = params.__dict__.get('PLATFORM', 'NO_PLATFORM_SPECIFIED')
        elif not os.path.exists(path):
            raise utils.PathError
        else:
            self.path = path
            self.platform = 'NO_PLATFORM_SPECIFIED'

        self.df = utils.file2df(self.path)

    def __str__(self):
        return self.platform

    def validate(self):
        pass



