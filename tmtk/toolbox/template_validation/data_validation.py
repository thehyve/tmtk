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
        :param self.tests_to_run: list containing function calls for data validation tests
        """
        self.data_df = data_df
        self.tree_df = tree_df
        self.sheet_name = sheet_name
        self.n_comment_lines = 0
        self.is_valid = True
        self.tests_to_run = [self.after_comments(),
                             self.check_encoding(),
                             self.mandatory_col(),
                             self.unique_col_names(),
                             self.col_name_in_tree_sheet()
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

    def mandatory_col(self):
        """Set self.is_valid = False if a subject identifier column called 'SUBJ_ID' is
        not present in the clinical data and give an error message if it is not.
        """
        if 'SUBJ_ID' not in self.data_df.columns:
            self.is_valid = False
            logger.error(" Mandatory column containing subject identifiers (SUBJ_ID) not detected "
                         "in clinical data '{}.".format(self.sheet_name))

    def unique_col_names(self):
        """Set self.is_valid = False if a double column name is found and give an
        error message specifying the duplicate column name(s).
        """
        columns = self.data_df.columns
        duplicate_columns = set(columns[columns.duplicated()])

        if duplicate_columns:
            self.is_valid = False
            logger.error(' Detected duplicate column name(s): \n\t' + '\n\t'.join(duplicate_columns))

    def col_name_in_tree_sheet(self):
        """Set self.can_continue = False if a column name in clinical data and tree structure
        sheet do not match. Gives an error message specifying which column name(s) do not match.
        :param tree_sheet_columns: list of entries in Tree structure sheet, Column name
        :param data_columns: list of column names in clinical data
        """
        for col in set(self.data_df.columns):
            if col != 'SUBJ_ID' and col not in set(self.tree_df['Column name']):
                logger.error(" Column name: '{}' not listed in Tree structure column: 'Column name'.".format(col))
                self.is_valid = False


def is_utf8(string):
    try:
        string.encode()
        return True
    except UnicodeDecodeError:
        return False
