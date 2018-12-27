import logging

logger = logging.getLogger(' Clinical data')


class DataValidator:

    def __init__(self, data_df, tree_df, sheet_name):
        """Creates object DataValidator that runs validation tests on clinical data and gives user-friendly
        error messages.

        :param self.data_df: clinical data in pandas data frame
        :param self.tree_df: tree structure in pandas data frame
        :param self.sheet_name: name of clinical data sheet
        :param self.n_comment_lines: stores index of first line in data sheet that is not a comment
        :param self.is_valid: boolean tracking if data passes validation steps
        :param self.tests_to_run: dict containing function calls for data validation tests
        """
        self.data_df = data_df
        self.tree_df = tree_df
        self.sheet_name = sheet_name
        self.n_comment_lines = 0
        self.is_valid = True
        self.tests_to_run = [self.after_comments(),
                             self.check_encoding()
                             ]

    def after_comments(self):
        """Determines where initial text with comments (instructions for data owner) ends, saves data_df without
        these comments to continue checking and assigns column names.
        """
        while str(self.data_df.iloc[self.n_comment_lines, 0]).startswith('#'):
            self.n_comment_lines += 1

        header = self.data_df.iloc[self.n_comment_lines]
        self.data_df = self.data_df[self.n_comment_lines + 1:]
        self.data_df = self.data_df.rename(columns=header)

    def check_encoding(self):
        """Iterate through data_df and check whether data can be encoded in UTF-8 and for # and \ within data.
        When data cannot be encoded or one of these characters is detected set self.is_valid = False and give error
        message with their location column name and row number.
        """
        forbidden_chars = ('#', '\\')

        for col_name, series in self.data_df.iteritems():
            for idx, value in series.iteritems():
                if not is_utf8(value):
                    logger.error(" Value in '{}' at column '{}', row: {} cannot be UTF-8 "
                                 "encoded.".format(self.sheet_name, col_name, idx + 1))
                if any((c in forbidden_chars) for c in value):
                    self.is_valid = False
                    logger.error(" Detected '#' or '\\' in '{}' at column: '{}', row: "
                                 "{}.".format(self.sheet_name, col_name, idx + 1))


def is_utf8(string):
    try:
        string.encode()
        return True
    except UnicodeDecodeError:
        return False
