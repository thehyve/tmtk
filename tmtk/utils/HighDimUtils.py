import os
import pandas as pd


def find_missing_annotations(annotation_series, data_series):
    """
    Inputs two pandas series, returns all missing annotations.

    :param annotation_series: the annotation that will be uploaded.
    :param data_series: series of genes that is in the datafile.
    :return: a new series with all missing annotations.
    """
    complement = data_series[~data_series.isin(annotation_series)]
    return list(complement)


def check_datafile_header_with_subjects(header_samples, mapping_samples):
    """
    Inputs two pandas series, returns all missing annotations.

    :param header_samples: samples from datafile header.
    :param mapping_samples: samples present in sample mapping file.
    :return: a dict with mismapped and excluded samples.
    """
    header_samples = pd.Series(header_samples)
    mapping_samples = pd.Series(mapping_samples)

    not_in_data_header = mapping_samples[~mapping_samples.isin(header_samples)]
    not_in_sample_mapping = header_samples[~header_samples.isin(mapping_samples)]
    intersection = header_samples[header_samples.isin(mapping_samples)]
    return {'not_in_datafile': set(not_in_data_header),
            'not_in_sample_mapping': set(not_in_sample_mapping),
            'intersection': set(intersection),
            }
