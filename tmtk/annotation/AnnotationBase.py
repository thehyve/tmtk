import os

from ..utils import Mappings, TransmartBatch, PathError, FileBase, ValidateMixin


class AnnotationBase(FileBase, ValidateMixin):
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
            self.params = params
        elif path and os.path.exists(path):
            self.path = path
            self.platform = 'NO_PLATFORM_SPECIFIED'
        else:
            raise PathError
        super().__init__()

    def __str__(self):
        return 'Annotations: {} ({})'.format(self.params.datatype, self.params.dirname)

    def __repr__(self):
        return 'Annotations: {} ({})'.format(self.params.datatype, self.params.dirname)

    @property
    def marker_type(self):
        return Mappings.annotation_marker_types.get(self.params.datatype)

    @property
    def load_to(self):
        return TransmartBatch(param=self.params.path,
                              items_expected=self._get_lazy_batch_items()
                              ).get_loading_namespace()

    def _get_lazy_batch_items(self):
        return {self.params.path: [self.path]}
