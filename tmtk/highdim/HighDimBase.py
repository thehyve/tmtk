import tmtk.utils as utils
from .SampleMapping import SampleMapping
from tmtk.annotation import ChromosomalRegions
import tmtk.toolbox as Toolbox
import pandas as pd
import os
from tmtk.utils import MessageCollector


class HighDimBase:
    """
    Base class for high dimensional data structures.
    """
    def __init__(self, params=None, path=None, parent=None):
        """

        :param params:
        :param path:
        :param parent:
        """
        if params and params.is_viable():
            self.params = params
            self.path = os.path.join(params.dirname, params.DATA_FILE)
        elif path and os.path.exists(self.path):
            self.path = path
        else:
            raise utils.PathError()

        self.df = utils.file2df(self.path)

        if hasattr(params, 'MAP_FILENAME'):
            self.sample_mapping = SampleMapping(os.path.join(params.dirname, params.MAP_FILENAME))
            self.sample_mapping_samples = self.sample_mapping.get_samples()
            self.platform = self.sample_mapping.get_platform()

            self._parent = parent
            if hasattr(self._parent, 'Annotations'):
                self.annotation_file = parent.find_annotation(self.platform)

    @property
    def header(self):
        return self.df.columns

    def validate(self, verbosity=2):
        """
        Validate high dimensional data object
        :param verbosity:
        :return:
        """
        messages = MessageCollector(verbosity=verbosity)
        messages.head("Validating {}".format(self.params.subdir))
        self._validate_header(messages)
        self._verify_sample_mapping(messages)

        if self.annotation_file:
            # Todo add check that first validates the annotation file.
            data_series = self.df.ix[:, 0]
            self._find_missing_annotation(annotation_series=self.annotation_file.biomarkers,
                                          data_series=data_series, messages=messages)

        messages.flush()
        return not messages.found_error

    def _check_header_extensions(self, messages):
        for h in self.header[1:]:
            try:
                count_type = h.rsplit('.', 1)[1]
            except IndexError:
                messages.error('Expected header with dot, but got {}.'.format(h))
                continue

            illegal_header_items = []
            if count_type not in self.allowed_header:
                illegal_header_items.append(count_type)
            if illegal_header_items:
                messages.error('Found illegal header items {}.'.
                               format(utils.summarise(illegal_header_items)))

    def _verify_sample_mapping(self, messages):
        samples_verified = utils.check_datafile_header_with_subjects(self.samples,
                                                                     self.sample_mapping_samples)

        not_in_datafile = samples_verified['not_in_datafile']
        if not_in_datafile:
            messages.error('Samples not in datafile: {}.'.
                           format(utils.summarise(not_in_datafile)))

        not_in_sample_mapping = samples_verified['not_in_sample_mapping']
        if not_in_sample_mapping:
            m = 'Samples not in mapping file: {}.'.format(utils.summarise(not_in_sample_mapping))
            if self.params.__dict__.get('SKIP_UNMAPPED_DATA', 'N') == 'Y':
                messages.warn(m)
            else:
                messages.error(m)

        intersection = samples_verified['intersection']
        if intersection:
            messages.info('Intersection of samples: {}.'.
                          format(utils.summarise(intersection)))

    def _find_missing_annotation(self, annotation_series=None, data_series=None, messages=None):
        """
        Checks for missing annotations.

        :param annotation_series:
        :param data_series:
        :return:
        """
        missing_annotations = utils.find_missing_annotations(annotation_series=annotation_series,
                                                             data_series=data_series)

        if not missing_annotations:
            return

        m = 'Missing annotations found: {}'.format(utils.summarise(missing_annotations))

        if self.params.__dict__.get('ALLOW_MISSING_ANNOTATIONS', 'N') == 'Y':
            messages.warn(m)
        else:
            messages.error(m)

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
