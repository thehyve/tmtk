import tmtk.utils as utils
from .Base import HighDimBase


class ReadCounts(HighDimBase):
    """
    Subclass for ReadCounts.
    """
    def validate(self):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks header if it contains only <samplecode>.(normalized)readcount.
        Also
        """
        self._validate_header()
        self._find_missing_annotation()

    def _validate_header(self):
        header = self.df.columns

        allowed = ['readcount', 'normalizedreadcount']

        message = self._check_header_extensions(allowed=allowed, header=header[1:])

        if message:
            utils.print_message_list(message)

    def _find_missing_annotation(self):
        """
        Checks for missing annotations.
        """
        biomarker_ids = self.annotation_file.df.ix[:, 8]

        utils.find_missing_annotations(annotation_series=biomarker_ids,
                                       data_series=self.df.ix[:0])
