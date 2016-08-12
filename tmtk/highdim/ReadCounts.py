from .HighDimBase import HighDimBase


class ReadCounts(HighDimBase):
    """
    Subclass for ReadCounts.
    """

    def _validate_specifics(self, messages):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks header if it contains only <samplecode>.(normalized)readcount.
        Also
        """
        self._check_header_extensions(messages)

    def remap_to(self, destination=None):
        """

        :param destination:
        :return:
        """
        return self._remap_to_chromosomal_regions(destination)

    @property
    def samples(self):
        return [h.rsplit('.', 1)[0] for h in self.header[1:]]

    @property
    def allowed_header(self):
        return ['readcount',
                'normalizedreadcount']
