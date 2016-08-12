import os
import tmtk.utils as utils


class AnnotationBase(utils.FileBase):
    """
    Base class for annotation files.
    """

    def __init__(self, params=None, path=None):
        """

        :param params:
        :param path:
        """
        if params and params.is_viable():
            self.path = os.path.join(params.dirname, params.ANNOTATIONS_FILE)
            self.platform = params.get('PLATFORM')
        elif path and os.path.exists(path):
            self.path = path
            self.platform = 'NO_PLATFORM_SPECIFIED'
        else:
            raise utils.PathError
        super().__init__()

    def __str__(self):
        return self.platform

    def validate(self, verbosity=2):
        pass
