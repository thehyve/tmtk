from .HighDimBase import HighDimBase


class Mirna(HighDimBase):
    """
    Base class for proteomics data.
    """

    def _validate_specifics(self, messages=None):
        """
        Makes checks to determine whether transmart-batch likes this file.
        """
        if self.header[0] != 'ID_REF':
            messages.warn('Expected "ID_REF", but got {} for {}'.format(self.header[0], self.path))

    @property
    def samples(self):
        return self.header[1:]
