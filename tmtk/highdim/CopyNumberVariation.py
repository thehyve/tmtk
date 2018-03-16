from .HighDimBase import HighDimBase
import tmtk.utils as utils


class CopyNumberVariation(HighDimBase):
    """
    Base class for copy number variation datatypes (aCGH, qDNAseq)
    """

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

    def _validate_probabilities(self):

        bad_regions = []
        bad_samples = []
        everything_okay = True

        for sample in set(self.samples):
            columns = self.header.str.contains(sample + '.prob')
            sample_df = self.df.iloc[:, columns].astype(float)
            not_full_nan = ~sample_df.isnull().all(axis=1)
            not_near_1 = ~sample_df.sum(axis=1).between(0.99, 1.01) & not_full_nan
            if any(not_near_1):
                everything_okay = False
                bad_samples.append(sample)
                [bad_regions.append(x) for x in self.df.loc[not_near_1, self.df.columns[0]]]  # Adds region ids to list.

        if not everything_okay:
            m = 'Samples ({}) where have regions where CNV probabilities do not approximate 1. ' \
                'Regions: {}.'.format(utils.summarise(bad_samples), utils.summarise(bad_regions))

            if self.params.get('PROB_IS_NOT_1', 'ERROR') == 'WARN':
                self.msgs.warning(m)
            else:
                self.msgs.error(m)
        else:
            self.msgs.okay('All probabilities approximate 1.')

    def _validate_header_extensions(self):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks whether header contains the <samplecode>.<probability_type>.
        """

        self._check_header_extensions()
