import pandas as pd
import os

from .SampleMapping import SampleMapping

from ..utils import FileBase, ValidateMixin, PathError, ClassError, TransmartBatch, summarise
from ..annotation import ChromosomalRegions


class HighDimBase(FileBase, ValidateMixin):
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
            raise PathError

        super().__init__()

        if hasattr(params, 'MAP_FILENAME'):
            self.sample_mapping = SampleMapping(os.path.join(params.dirname, params.MAP_FILENAME))
            self.platform = self.sample_mapping.platform

            self._parent = parent
            if hasattr(self._parent, 'Annotations'):
                self.annotation_file = parent.find_annotation(self.platform)

    def __str__(self):
        return 'HighDim: {} ({})'.format(self.params.datatype, self.params.dirname)

    def __repr__(self):
        return 'HighDim: {} ({})'.format(self.params.datatype, self.params.dirname)

    def _check_header_extensions(self):

        illegal_header_items = []

        for h in self.header[1:]:
            try:
                count_type = h.rsplit('.', 1)[1]
            except IndexError:
                self.msgs.error('Expected header with dot, but got {}.'.format(h))
                continue

            # Add count_type to illegal items if not allowed.
            if count_type not in self.allowed_header:
                illegal_header_items.append(count_type)

        # Create list of illegal header items.
        if illegal_header_items:
            self.msgs.error('Found illegal header items.', warning_list=illegal_header_items)
        else:
            self.msgs.okay('Header extensions are okay!')

    def _remap_to_chromosomal_regions(self, destination=None):
        """

        :param destination:
        :return:
        """
        from ..toolbox import remap_chromosomal_regions

        if not self.annotation_file:
            raise Exception

        if isinstance(destination, ChromosomalRegions):
            destination = destination.df
        elif not isinstance(destination, pd.DataFrame):
            raise ClassError(found=type(destination), expected='pd.DataFrame, or ChromosomalRegions')

        remapped = remap_chromosomal_regions(datafile=self.df,
                                             origin_platform=self.annotation_file.df,
                                             destination_platform=destination)
        return remapped

    @property
    def load_to(self):
        return TransmartBatch(self.params.path,
                              items_expected=self._get_lazy_batch_items()
                              ).get_loading_namespace()

    def _get_lazy_batch_items(self):
        return {self.params.path: (len(self.sample_mapping.samples), self.path)}

    def _validate_missing_annotation(self):
        missing_annotations = list(self.df.iloc[:, 0][~self.df.iloc[:, 0].isin(self.annotation_file.biomarkers)])

        if missing_annotations:
            self.msgs.warning('Missing annotations found.', warning_list=missing_annotations)
        else:
            self.msgs.okay('All data items have associated annotations.')

    def _validate_missing_data_items(self):
        missing_data = list(self.annotation_file.biomarkers[~self.annotation_file.biomarkers.isin(self.df.iloc[:, 0])])

        if not missing_data:
            self.msgs.okay('The entire annotation platform seems to have associated data.')
            return

        msg = 'Data file has less data than annotations.'

        if self.params.get('ALLOW_MISSING_ANNOTATIONS', 'N') == 'Y':
            self.msgs.warning(msg, warning_list=missing_data)
        else:
            self.msgs.error(msg, warning_list=missing_data)

    def _validate_annotation_file(self):

        if hasattr(self, 'annotation_file'):
            if not self.annotation_file:
                self.msgs.error('No annotation file found for {}.'.format(self.platform))
            else:
                self.msgs.okay('Annotation file found for {}!'.format(self.platform))

    def _validate_sample_mapping(self):
        header_samples = pd.Series(self.samples)
        mapping_samples = pd.Series(self.sample_mapping.samples)

        not_in_datafile = set(mapping_samples[~mapping_samples.isin(header_samples)])
        not_in_sample_mapping = set(header_samples[~header_samples.isin(mapping_samples)])
        intersection = set(header_samples[header_samples.isin(mapping_samples)])

        if not_in_datafile:
            self.msgs.error('Samples not in datafile: {}!'.format(summarise(not_in_datafile)),
                            warning_list=not_in_datafile)

        if not_in_sample_mapping:
            if self.params.get('SKIP_UNMAPPED_DATA', 'N') == 'Y':
                self.msgs.warning('Samples not in mapping file: {}.'.format(summarise(not_in_sample_mapping)),
                                  warning_list=not_in_sample_mapping)
            else:
                self.msgs.error('Samples not in mapping file: {}.'.format(summarise(not_in_sample_mapping)),
                                warning_list=not_in_sample_mapping)

        if intersection:
            self.msgs.info('Intersection of samples: {}.'.format(summarise(intersection)),
                           warning_list=intersection)

    def _validate_sample_mapping_study_id(self):
        if self.sample_mapping.study_id != self._parent.study_id:
            m = 'Study_id in ({}) does not match ({}) in study.params'.\
                format(self.sample_mapping.study_id, self._parent.study_id)
            self.msgs.error(m)
        else:
            self.msgs.okay('STUDY_ID as expected from study.params.')
