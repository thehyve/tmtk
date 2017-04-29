import os

import IPython
import pandas as pd


class TemplateException(Exception):
    def __init__(self, Exception):
        self.epilogue(huge_succes=False)

    @staticmethod
    def epilogue(huge_succes=True):
        (ID, start) = "HKIbIC9H_Kg", 9
        if huge_succes:
            (ID, start) = "S9x6GMM4UWw", 0
        IPython.display.display(IPython.display.YouTubeVideo(ID, autoplay=1, width=1, height=1, start=start))


def check_source_dir(source_path):
    if not os.path.isdir(source_path):
        raise TemplateException("Directory does not exist: {0}".format(source_path))
    elif not os.access(source_path, os.R_OK):
        raise TemplateException("You do not have read access for this directory: {0}".format(source_path))


def check_output_dir(output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print("[INFO] Created output directory at: {0}".format(output_path))
    if not os.access(output_path, os.W_OK):
        raise TemplateException("No write access for given directory path: {0}".format(output_path))


def check_uniformity(data_series, allow_nan=False):
    for item in data_series:
        if not allow_nan and pd.isnull(item).any():
            raise TemplateException("Mandatory data series '{0}' has missing values: ".format(item.name) +
                                    str(set(item)))
        values = set(item)
        if len(values) != 1:
            raise TemplateException(("Multiple values detected in data series '{0}' expected" +
                                     " to be uniform: ").format(item.name) + str(values))


def check_uniqueness(data_series):
    for item in data_series:
        duplicates = item[item.duplicated(keep=False)]
        if len(duplicates) != 0:
            raise TemplateException(("Duplicates detected in data series '{0}' that should be " +
                                     "unique: ").format(item.name) + str(set(duplicates)))


def list_length(item_list, expected):
    length = len(item_list)
    correct_length = length == expected
    if not correct_length:
        error_message = "Incorrect list length: {0}, expected {1}, for list: {2}".format(length, expected, item_list)
        raise TemplateException(error_message)
    return True


def empty_df(df, mandatory=True, df_name="data frame", workbook_name="workbook"):
    empty = False
    if df.empty:
        empty = True
        message = "Empty {0} detected in {1}.".format(df_name, workbook_name)
        if mandatory:
            raise TemplateException("[Error] " + message)
        else:
            print("[WARNING] " + message)
    return empty
