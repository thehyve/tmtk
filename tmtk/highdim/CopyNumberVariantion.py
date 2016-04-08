from tmtk.highdim import HighDimBase
import tmtk.utils as utils


class CopyNumberVariation(HighDimBase):
    """
    Base class for copy number variation datatypes (aCGH, qDNAseq)
    """
    def validate(self):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks whether header contains the <samplecode>.<probability_type>.
        """
        self._validate_header()

        if self.annotation_file:
            self._find_missing_annotation()

    def _validate_header(self):
        header = self.df.columns

        allowed = ['probhomloss',
                   'probloss',
                   'probnorm',
                   'probgain',
                   'probamp',
                   'segmented',
                   'chip',
                   'flag',
                   ]

        message = self._check_header_extensions(allowed=allowed, header=header[1:])

        utils.print_message_list(message)

    def _find_missing_annotation(self):
        """
        Checks for missing annotations.
        """
        biomarker_ids = self.annotation_file.df.ix[:, 8]

        message = utils.find_missing_annotations(annotation_series=biomarker_ids,
                                                 data_series=self.df.ix[:0])
        utils.print_message_list(message)
