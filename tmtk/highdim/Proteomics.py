from .HighDimBase import HighDimBase


class Proteomics(HighDimBase):
    """
    Base class for proteomics data.
    """

    def _validate_specifics(self):
        """
        Makes checks to determine whether transmart-batch likes this file.
        """
        if self.header[0] != 'REF_ID':
            self.msgs.warning('Expected "REF_ID", but got {} for {}'.format(self.header[0], self.path))

    @property
    def samples(self):
        return self.header[1:]
