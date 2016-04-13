import tmtk.utils as utils
from .HighDimBase import HighDimBase


class ReadCounts(HighDimBase):
    """
    Subclass for ReadCounts.
    """
    def validate(self, verbosity=2):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks header if it contains only <samplecode>.(normalized)readcount.
        Also
        """
        self._validate_header()
        if self.annotation_file:
            biomarker_ids = self.annotation_file.df.ix[:, 1]
            data_series = self.df.ix[:, 0]
            self._find_missing_annotation(annotation_series=biomarker_ids, data_series=data_series)

    def _validate_header(self):
        header = self.df.columns

        allowed = ['readcount', 'normalizedreadcount']

        message = self._check_header_extensions(allowed=allowed, header=header[1:])

        if message:
            utils.print_message_list(message)

    def remap_to(self, destination=None):
        """

        :param destination:
        :return:
        """
        return self._remap_to_chromosomal_regions(destination)
