from .HighDimBase import HighDimBase


class Expression(HighDimBase):
    """
    Base class for microarray mRNA expression data.
    """

    def _validate_id_ref(self):
        """
        Makes checks to determine whether transmart-batch likes this file.
        """
        if self.header[0] != 'ID_REF':
            self.msgs.warning('Expected "ID_REF", but got {} for {}'.format(self.header[0], self.path))

    @property
    def samples(self):
        return self.header[1:]
