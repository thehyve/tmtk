from .HighDimBase import HighDimBase


class Proteomics(HighDimBase):
    """
    Base class for proteomics data.
    """

    def _validate_specifics(self, messages=None):
        """
        Makes checks to determine whether transmart-batch likes this file.
        """
        if self.header[0] != 'REF_ID':
            messages.warn('Expected "REF_ID", but got {} for {}'.format(self.header[0], self.path))

    @property
    def samples(self):
        return self.header[1:]
