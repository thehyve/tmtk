from tmtk.highdim import HighDimBase
import tmtk.utils as utils


class Proteomics(HighDimBase):
    """
    Base class for proteomics data.
    """
    def validate(self, verbosity=2):
        """
        Makes checks to determine whether transmart-batch likes this file.
        """
        self._validate_header()

        if self.annotation_file:
            # Todo add check that first validates the annotation file.
            biomarker_ids = self.annotation_file.df['probesetID']
            data_series = self.df.ix[:, 0]
            self._find_missing_annotation(annotation_series=biomarker_ids, data_series=data_series)

    def _validate_header(self):
        header = self.df.columns

        message = self._check_header_extensions(header=header[1:])

        if header[0] != 'REF_ID':
            message.append('Expected "REF_ID", but got {} for {}'.format(header[0], self.path))

        utils.print_message_list(message)

