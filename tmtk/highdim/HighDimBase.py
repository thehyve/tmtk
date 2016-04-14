import tmtk.utils as utils
from .SampleMapping import SampleMapping
from tmtk.annotation import ChromosomalRegions
import tmtk.toolbox as Toolbox
import pandas as pd
import os


class HighDimBase:
    """
    Base class for high dimensional data structures.
    """
    def __init__(self, p=None, path=None, parent=None):
        """

        :param p:
        :param path:
        :param parent:
        """
        if p and p.is_viable():
            self.params = p
            self.path = os.path.join(p.dirname, p.DATA_FILE)
        elif path and os.path.exists(self.path):
            self.path = path
        else:
            raise utils.PathError()

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

        :param annotation_series:
        :param data_series:
        :return:
        """
        missing_annotations = utils.find_missing_annotations(annotation_series=annotation_series,
                                                             data_series=data_series)

        utils.print_message_list(missing_annotations, 'Missing annotations:')

    def _remap_to_chromosomal_regions(self, destination=None):
        """

        :param destination:
        :return:
        """
        if not self.annotation_file:
            raise Exception

        if isinstance(destination, ChromosomalRegions):
            destination = destination.df
        elif not isinstance(destination, pd.DataFrame):
            raise utils.ClassError(found=type(destination),
                                   expected='pd.DataFrame, or ChromosomalRegions')

        remapped = Toolbox.remap_chromosomal_regions(datafile=self.df,
                                                     origin_platform=self.annotation_file.df,
                                                     destination_platform=destination)
        return remapped
