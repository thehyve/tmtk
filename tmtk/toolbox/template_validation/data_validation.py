import logging

logger = logging.getLogger(' Clinical data')


class DataValidator:

    def __init__(self, data_df, tree_df, sheet_name):
        """Creates object DataValidator that runs validation tests on clinical data and gives user-friendly
        error messages.

        :param self.data_df: clinical data in pandas data frame
        :param self.end_comments: stores index of first line in data sheet that is not a comment
        :param self.is_valid: boolean tracking if data passes validation steps
        :param self.tests_to_run: dict containing function calls for data validation tests
        """
        self.data_df = data_df
        self.tree_df = tree_df
        self.sheet_name = sheet_name
        self.end_comments = 0
        self.is_valid = True
        self.tests_to_run = {}
