from tmtk.highdim import HighDimBase
import tmtk.utils as utils


class CopyNumberVariation(HighDimBase):
    """
    Base class for copy number variation datatypes (aCGH, qDNAseq)
    """
    def _validate_header(self,  messages):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks whether header contains the <samplecode>.<probability_type>.
        """

        self._check_header_extensions(messages)

    def _validate_data_file(self):
        self.df.ix[:, 1:].applymap(str.isalpha())

    @property
    def samples(self):
        return [h.rsplit('.', 1)[0] for h in self.header[1:]]

    @property
    def allowed_header(self):
        return ['probhomloss',
                'probloss',
                'probnorm',
                'probgain',
                'probamp',
                'segmented',
                'chip',
                'flag',
                ]

    def remap_to(self, destination=None):
        """

        :param destination:
        :return:
        """
        return self._remap_to_chromosomal_regions(destination)
