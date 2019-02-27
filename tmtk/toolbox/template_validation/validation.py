import logging
import pandas as pd


class Validator:

    def __init__(self, df):
        """
        Creates object Validator that runs common validation steps for the loaded sheet or file.

        :param self.df: one of the sheets (or files referred to) in the template in a pandas data frame
        :param self.n_comment_lines: stores index of first line in data sheet that is not a comment
        :param self.is_valid: boolean tracking if data passes validation steps
        :param self.can_continue: boolean tracking if validation steps can continue without issues in next tests
        :param self.tests_to_run: list containing function calls for data validation tests
        :param self.logger: Logger instance
        :param self.logger.setLevel: sets loggers level of printing
        :param self.mandatory_columns: mandatory columns for a sheet
        :param self.data_source:
        """
        self.df = df
        self.n_comment_lines = 0
        self.is_valid = True
        self.can_continue = True
        self.tests_to_run = (test for test in [])
        self.logger = logging.getLogger('')
        self.logger.setLevel(level=logging.DEBUG)
        self.mandatory_columns = []
        self.data_source = ''

    def validate_sheet(self):
        """ Iterates over tests_to_run while no issues are encountered that would interfere with following
        validation steps
        """
        while self.can_continue:
            next_test = next(self.tests_to_run, None)
            if next_test:
                next_test()
            else:
                return

    def after_comments(self):
        """Determines where initial text with comments (instructions for data owner) ends, saves tree_df without
        these comments to continue checking and assigns column names.
        """
        while str(self.df.iloc[self.n_comment_lines, 0]).startswith('#'):
            self.n_comment_lines += 1

        header = self.df.iloc[self.n_comment_lines]
        self.df = self.df[self.n_comment_lines + 1:]
        self.df = self.df.rename(columns=header)

    def check_forbidden_chars(self):
        """Iterate through df and check for #, \ and newlines (\n or \r)  within data. When one of these characters or
         character sets is detected set self.is_valid = False and give error message with their location column name
         and row number.
        """
        forbidden_chars = ('#', '\\', '\n', '\r')

        for col_name, series in self.df.iteritems():
            for idx, value in series.iteritems():
                if any((c in forbidden_chars) for c in str(value)):
                    self.is_valid = False
                    self.logger.error(" Detected '#', '\\' or new line at column: '{}', row: {}."
                                      .format(col_name, idx + 1))

    def check_whitespace(self):
        """Checks whether there is any whitespace at the start or end of a value.
        """
        # check values in columns
        for col_name, series in self.df.iteritems():
            if col_name.startswith(' ') or col_name.endswith(' '):
                self.can_continue = False
                self.is_valid = False
                self.logger.error(" Detected whitespace at start or end of column header: '{}'.".format(col_name))
            for idx, value in series.dropna().iteritems():
                if str(value).startswith(' ') or str(value).endswith(' '):
                    self.is_valid = False
                    self.logger.error(" Detected whitespace at start or end of value in column: '{}', row: {}."
                                      .format(col_name, idx + 1))

    def check_mandatory_columns(self):
        """ Checks whether mandatory columns are present. If one or more mandatory columns are absent self.can_continue
        is set to False and validation of this sheet cannot go on.
        """
        missing_columns = [col_name for col_name in self.mandatory_columns if col_name not in self.df.columns]

        if missing_columns:
            self.can_continue = False
            self.is_valid = False
            self.logger.error(' Missing the following mandatory columns:\n\t' + '\n\t'.join(missing_columns))

    def unique_col_names(self):
        """Set self.is_valid = False if a double column name is found and give an
        error message specifying the duplicate column name(s).
        """
        columns = self.df.columns
        duplicate_columns = set(columns[columns.duplicated()])

        if duplicate_columns:
            self.can_continue = False
            self.is_valid = False
            if self.data_source == '':
                self.logger.error(" Detected duplicate column name(s): \n\t" + "\n\t".join(duplicate_columns))
            else:
                self.logger.error(" Detected duplicate column name(s) in '" + self.data_source + "': \n\t" +
                                  "\n\t".join(duplicate_columns))
