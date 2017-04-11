import os

import IPython
import pandas as pd

class TemplateException(Exception):
    def __init__(self, Exception):
        self.epilogue()

    def epilogue(self):
        (ID, start) = "HKIbIC9H_Kg", 9
        IPython.display.display(IPython.display.YouTubeVideo(ID, autoplay=1, width=0, height=0, start=start))


class Validity:

    @staticmethod
    def check_source_dir(source_path):
        if not os.path.isdir(source_path):
            raise TemplateException("Directory does not exist: {0}".format(source_path))
        elif not os.access(source_path, os.R_OK):
            raise TemplateException("You do not have read access for this directory: {0}".format(source_path))

    @staticmethod
    def check_output_dir(output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print("[INFO] Created output directory at: {0}".format(output_path))
        if not os.access(output_path, os.W_OK):
            raise TemplateException("No write access for given directory path: {0}".format(output_path))

    @staticmethod
    def check_uniformity(data_series, allow_nan=False):
        for item in data_series:
            if not allow_nan and pd.isnull(item).any():
                raise TemplateException("Mandatory data series '{0}' has missing values: ".format(item.name) +
                                        str(set(item)))
            values = set(item)
            if len(values) != 1:
                raise TemplateException(("Multiple values detected in data series '{0}' expected" +
                                         " to be uniform: ").format(item.name) + str(values))

    @staticmethod
    def check_uniqueness(data_series):
        for item in data_series:
            duplicates = item[item.duplicated(keep=False)]
            if len(duplicates) != 0:
                raise TemplateException(("Duplicates detected in data series '{0}' that should be " +
                                         "unique: ").format(item.name) + str(set(duplicates)))

    @staticmethod
    def list_length(item_list, expected):
        length = len(item_list)
        correct_length = length == expected
        if not correct_length:
            error_message = "Incorrect list length: {0}, expected: {1}".format(length, expected)
            raise TemplateException(error_message)
        return True