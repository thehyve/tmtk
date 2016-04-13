from tmtk.highdim import HighDimBase
import tmtk.utils as utils


class CopyNumberVariation(HighDimBase):
    """
    Base class for copy number variation datatypes (aCGH, qDNAseq)
    """
    def validate(self, verbosity=2):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks whether header contains the <samplecode>.<probability_type>.
        """
        self._validate_header()

        if self.annotation_file:
            biomarker_ids = self.annotation_file.df.ix[:, 1]
            data_series = self.df.ix[:, 0]
            self._find_missing_annotation(annotation_series=biomarker_ids, data_series=data_series)

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

    def remap_to(self, destination=None):
        """

        :param destination:
        :return:
        """
        return self._remap_to_chromosomal_regions(destination)
