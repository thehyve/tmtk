from tmtk.highdim import HighDimBase
import tmtk.utils as utils


class Expression(HighDimBase):
    """
    Base class for microarray mRNA expression data.
    """
    def _validate_header(self, messages):
        """
        Makes checks to determine whether transmart-batch likes this file.
        """
        if self.header[0] != 'REF_ID':
            messages.error('Expected "REF_ID", but got {} for {}'.format(self.header[0], self.path))


    @property
    def samples(self):
        return self.header[1:]
