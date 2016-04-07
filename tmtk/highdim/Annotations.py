import os
import tmtk.utils as utils


class AnnotationFile(object):
    """
    Base class for annotation files.

    :param path: path to annotation file.
    """
    def __init__(self, path=None):
        if not os.path.exists(path):
            raise utils.PathError
        self.path = path
        self.df = utils.file2df(self.path)

    def validate(self):
        pass


