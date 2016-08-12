from .HighDimBase import HighDimBase
import tmtk.utils as utils


class CopyNumberVariation(HighDimBase):
    """
    Base class for copy number variation datatypes (aCGH, qDNAseq)
    """

    def _validate_specifics(self, messages):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks whether header contains the <samplecode>.<probability_type>.
        """

        if self._check_header_extensions(messages):
            self._validate_probabilities(messages)

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

    def _validate_probabilities(self, messages):

        bad_regions = []
        bad_samples = []
        everything_okay = True

        for sample in set(self.samples):
            columns = self.header.str.contains(sample + '.prob')
            sample_df = self.df.ix[:, columns].astype(float)
            sample_df = sample_df.dropna()
            not_near_1 = ~sample_df.sum(axis=1).between(0.99, 1.01)
            if any(not_near_1):
                everything_okay = False
                bad_samples.append(sample)
                [bad_regions.append(x) for x in
                 self.df.ix[not_near_1, 0]]  # Adds region ids to list.

        if not everything_okay:
            m = 'Samples ({}) where have regions where CNV probabilities do not approximate 1. ' \
                'Regions: {}.'.format(utils.summarise(bad_samples), utils.summarise(bad_regions))

            if self.params.get('PROB_IS_NOT_1', 'ERROR') == 'WARN':
                messages.warn(m)
            else:
                messages.error(m)
        else:
            messages.okay('All probabilities approximate 1.')
        return everything_okay
