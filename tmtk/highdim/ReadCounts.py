import os
import tmtk.utils as utils
from .SampleMapping import SampleMapping


class ReadCounts(object):
    """
    Base class for RNAseq read counts
    """
    def __init__(self, p):
        self.path = os.path.join(p.dirname, p.DATA_FILE)
        if not os.path.exists(self.path):
            raise utils.PathError(self.path)
        self.df = utils.file2df(self.path)
        self.sample_mapping = SampleMapping(os.path.join(p.dirname, p.MAP_FILENAME))
        self.sample_mapping_samples = self.sample_mapping.df.ix[:, 3]
        self.platform = self.sample_mapping.df.ix[0, 4]

    def validate(self):
        """
        Makes checks to determine whether transmart-batch likes this file.
        Checks header starts with REGION_NAME and contains only <samplecode>.(normalized)readcount.
        """
        self._validate_header()
        self._find_missing_annotation()

    def _validate_header(self):
        header = self.df.columns

        message = []
        samples = []
        for h in header[1:]:
            sample, count_type = h.rsplit('.', 1)
            if count_type not in ['readcount', 'normalizedreadcount']:
                message.append('Found header item {}, when expecting "readcount"'
                               ' or "normalizedreadcount".\n'.format(h))
            samples.append(sample)

        sample_checking_dict = utils.check_datafile_header_with_subjects(
            samples, self.sample_mapping_samples)

        if sample_checking_dict['excluded']:
            message.append('Excluded samples: {}.\n'.format(sample_checking_dict['excluded']))

        if sample_checking_dict['mismapped']:
            message.append('Mismapped samples: {}.\n'.format(sample_checking_dict['mismapped']))

        if message:
            print('Everything okay.')
        else:
            print(message)

    def _find_missing_annotation(self):
        """
        Checks for missing annotations.
        """
        pass
        # utils.find_missing_annotations(annotation_series=self.
        #                                data_series=self.df.ix[:0])
