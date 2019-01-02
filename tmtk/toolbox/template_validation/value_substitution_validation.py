import logging
import os
import pandas as pd

logger = logging.getLogger(" Value substitution sheet")
logger.setLevel(logging.DEBUG)


class ValueSubstitutionValidator:

    def __init__(self, value_substitution_df, source_dir, template):
        """Creates object ValueSubstitutionValidator that runs validation tests on value substitution sheet and
        gives user-friendly error messages.

        :param self.value_substitution_df: value substitution sheet in pandas data frame
        :param self.is_valid: boolean tracking if data passes validation steps
        """
        self.value_substitution_df = value_substitution_df
        self.source_dir = source_dir
        self.template = template
        self.n_comment_lines = 0
        self.is_valid = True
        self.can_continue = True
        self.tests_to_run = (test for test in
                             [self.after_comments,
                              self.mandatory_columns,
                              self.data_in_columns,
                              self.no_comment_or_backslash
                              ])

        self.validate_value_substitution_sheet()

    def validate_value_substitution_sheet(self):
        """ Iterates over tests_to_run while no issues are encountered that would interfere with following
        validation steps"""
        while self.can_continue:
            next_test = next(self.tests_to_run, None)
            if next_test:
                next_test()
            else:
                return

    def after_comments(self):
        """Determines where initial text with comments (instructions for data owner) ends, saves value_substitution_df
        without these comments to continue checking and assigns column names.
        """
        while str(self.value_substitution_df.iloc[self.n_comment_lines, 0]).startswith('#'):
            self.n_comment_lines += 1

        header = self.value_substitution_df.iloc[self.n_comment_lines]
        self.value_substitution_df = self.value_substitution_df[self.n_comment_lines + 1:]
        self.value_substitution_df = self.value_substitution_df.rename(columns=header)

    def mandatory_columns(self):
        """ Checks whether mandatory columns are present. If one or more mandatory columns are absent self.can_continue
        is set to False and validation of this sheet cannot go on.
        """
        mandatory_columns = set(['Sheet name/File name', 'Column name', 'From value', 'To value'])

        missing_columns = [col_name for col_name in mandatory_columns if col_name not in
                           self.value_substitution_df.columns]

        if missing_columns:
            self.can_continue = False
            self.is_valid = False
            logger.error(' Missing the following mandatory columns:\n\t' + '\n\t'.join(missing_columns))

    def data_in_columns(self):
        """ Checks whether there is data in the columns. If there is no data, the next validation steps are not
        executed.
        """
        if len(self.value_substitution_df) == 0:
            self.can_continue = False

    def no_comment_or_backslash(self):
        """Iterate through data_df and check for # and \ within data. When one of these characters is detected
        set self.is_valid = False and give error message with their location column name and row number.
        """
        forbidden_chars = ('#', '\\')

        for col_name, series in self.value_substitution_df.iteritems():
            for idx, value in series.iteritems():
                if any((c in forbidden_chars) for c in str(value)):
                    self.is_valid = False
                    logger.error(" Detected '#' or '\\' at column: '{}', row: {}.".format(col_name, idx + 1))
