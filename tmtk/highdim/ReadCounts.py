from .HighDimBase import HighDimBase


class ReadCounts(HighDimBase):
    """
    Subclass for ReadCounts.
    """

    def _validate_header_extensions(self):
        self._check_header_extensions()

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
