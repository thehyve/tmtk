import logging

logger = logging.getLogger('Clinical data')


class DataValidator:

    def __init__(self, data_df, tree_df, sheet_name):
        """Creates object DataValidator that runs validation tests on clinical data and gives user-friendly
        error messages.

        :param self.data_df: clinical data in pandas data frame
        :param self.tree_df: tree structure in pandas data frame
        :param self.sheet_name: name of clinical data sheet
        :param self.end_comments: stores index of first line in data sheet that is not a comment
        :param self.is_valid: boolean tracking if data passes validation steps
        :param self.tests_to_run: dict containing function calls for data validation tests
        """
        self.data_df = data_df
        self.tree_df = tree_df
        self.sheet_name = sheet_name
        self.end_comments = 0
        self.is_valid = True
        self.tests_to_run = {'1': self.after_comments(),
                             '2': self.no_special_characters()
                             }

    def after_comments(self):
        """Determines where initial text with comments (instructions for data owner) ends, saves data_df without
        these comments to continue checking and assigns column names.
        """
        i = 0
        while str(self.data_df.iloc[i, 0]).startswith('#'):
            i += 1

        if i != 0:
            self.end_comments = i

        header = self.data_df.iloc[i]
        self.data_df = self.data_df[i + 1:]
        self.data_df = self.data_df.rename(columns=header)

    def no_special_characters(self):
        """Iterate through data_df and check for special characters within data. When special characters are detected
        set self.can_continue = False and give error message with their location column name and row number.
        """
        chars = ('#', '+', '>', '<', '*', '&', '^', '%', '\\', 'α', 'β', '—', '–')
        enter_tab = ('\n', '\t')
        for i in range(len(self.data_df.columns)):
            col_name = self.data_df.columns.values[i]

            for j in range(len(self.data_df)):

                if any((c in chars) for c in str(self.data_df.iloc[j, i])):
                    self.is_valid = False
                    logger.error("Detected special character in '{}' at column: '{}', row: {}.".format(
                        self.sheet_name, col_name, str(j + 3 + self.end_comments)))

                if '\xa0' in str(self.data_df.iloc[j, i]):
                    self.is_valid = False
                    logger.error("Detected non-breaking space in '{}' at column: '{}', row: {}. ".format
                                 (self.sheet_name, col_name, str(j + 3 + self.end_comments)))

                if any((e_t in enter_tab) for e_t in str(self.data_df.iloc[j, i])):
                    self.is_valid = False
                    logger.error("Detected enter or tab in '{}' at column: '{}', row: {}. ".format
                                 (self.sheet_name, col_name, str(j + 3 + self.end_comments)))
