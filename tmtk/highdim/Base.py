import tmtk.utils as utils
from .SampleMapping import SampleMapping
import os


class HighDimBase:
    """
    Base class for high dimensional data structures.
    """
    def __init__(self, p, parent=None):
        self.path = os.path.join(p.dirname, p.DATA_FILE)

        if not os.path.exists(self.path):
            raise utils.PathError(self.path)

        self.df = utils.file2df(self.path)

        if hasattr(p, 'MAP_FILENAME'):
            self.sample_mapping = SampleMapping(os.path.join(p.dirname, p.MAP_FILENAME))
            self.sample_mapping_samples = self.sample_mapping.get_samples()
            self.platform = self.sample_mapping.get_platform()

            self._parent = parent
            if hasattr(self._parent, 'Annotations'):
                self.annotation_file = parent.find_annotation(self.platform)

    def _check_header_extensions(self, allowed=None, header=None):
        """

        :param allowed: list of items that are allowed as count types. If None, assume only samples.
        :param header: list of header items to be checked.
        :return: message list, hopefully empty.
        """
        samples = []
        message = []
        for h in header:
            if not allowed:
                samples.append(h)
            else:
                sample, count_type = h.rsplit('.', 1)
                samples.append(sample)
                if count_type not in allowed:
                    message.append('Found incorrect header item {}, for {}.\n'.format(h, self.path))

        sample_checking_dict = utils.check_datafile_header_with_subjects(
            samples, self.sample_mapping_samples)

        not_in_datafile = sample_checking_dict['not_in_datafile']
        if not_in_datafile:
            message.append('Samples not in datafile: {}.\n'.format(not_in_datafile))

        not_in_sample_mapping = sample_checking_dict['not_in_sample_mapping']
        if not_in_sample_mapping:
            message.append('Samples not in mapping file: {}.\n'.format(not_in_sample_mapping))

        intersection = sample_checking_dict['intersection']
        if intersection:
            message.append('Intersection of samples: {}.\n'.format(intersection))

        return message

    def _find_missing_annotation(self, annotation_series=None, data_series=None):
        """
        Checks for missing annotations.
        """
        missing_annotations = utils.find_missing_annotations(annotation_series=annotation_series,
                                                             data_series=data_series)

        utils.print_message_list(missing_annotations, 'Missing annotations:')
