import logging
import pandas as pd

logger = logging.getLogger(' Tree structure')
logger.setLevel(logging.DEBUG)


class TreeValidator:

    def __init__(self, tree_df):
        """" Creates object TreeValidator that runs validation tests on tree structure sheet and
        gives user-friendly error messages.

        :param self.tree_df: value substitution sheet in pandas data frame
        :param self.is_valid: boolean tracking if data passes validation steps
        :param self.can_continue: boolean tracking if validation steps can continue without issues in next tests
        :param self.n_comment_lines: stores index of first line in data sheet that is not a comment
        :param self.tests_to_run: list containing function calls for data validation tests
        """
        self.tree_df = tree_df
        self.is_valid = True
        self.can_continue = True
        self.n_comment_lines = 0
        self.tests_to_run = (test for test in
                             [self.after_comments,
                              self.no_comment_or_backslash,
                              self.mandatory_columns,
                              self.unique_col_names,
                              self.transmart_data_types,
                              self.data_source_referenced,
                              self.consecutive_levels,
                              self.check_level_1
                              ])

        self.validate_tree_sheet()

    def validate_tree_sheet(self):
        """ Iterates over tests_to_run while no issues are encountered that would interfere with following
        validation steps"""
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
        while str(self.tree_df.iloc[self.n_comment_lines, 0]).startswith('#'):
            self.n_comment_lines += 1

        header = self.tree_df.iloc[self.n_comment_lines]
        self.tree_df = self.tree_df[self.n_comment_lines + 1:]
        self.tree_df = self.tree_df.rename(columns=header)

    def no_comment_or_backslash(self):
        """Iterate through data_df and check for # and \ within data. When one of these characters is detected
        set self.is_valid = False and give error message with their location column name and row number.
        """
        forbidden_chars = ('#', '\\')

        for col_name, series in self.tree_df.iteritems():
            for idx, value in series.iteritems():
                if any((c in forbidden_chars) for c in str(value)):
                    self.is_valid = False
                    logger.error(" Detected '#' or '\\' at column: '{}', row: {}.".format(col_name, idx + 1))

    def mandatory_columns(self):
        """ Checks whether mandatory column names are present in the tree structure sheet.
        """
        mandatory_columns = ['tranSMART data type', 'Sheet name/File name', 'Column name', 'Level 1',
                             'Level 1 metadata tag', 'Level 1 metadata value']

        missing_columns = [col for col in mandatory_columns if col not in self.tree_df.columns]

        for i in range(2, len(self.tree_df.columns)):
            metadata_tag = 'Level ' + str(i) + ' metadata tag'
            metadata_value = 'Level ' + str(i) + ' metadata value'
            level = 'Level ' + str(i)

            # check if 'Level' column has corresponding 'metadata tag' and 'metadata value' columns:
            if level in self.tree_df.columns:
                if metadata_tag not in self.tree_df.columns:
                    missing_columns.append(metadata_tag)
                if 'Level ' + str(i) + ' metadata value' not in self.tree_df.columns:
                    missing_columns.append(metadata_value)

            # check if 'metadata tag' and 'metadata value' columns have a corresponding 'Level' column:
            if metadata_tag in self.tree_df.columns and metadata_value in self.tree_df.columns:
                if level not in self.tree_df.columns:
                    missing_columns.append(level)

        if missing_columns:
            self.is_valid = False
            self.can_continue = False
            logger.error(' Missing the following mandatory columns:\n\t' + '\n\t'.join(missing_columns))

    def unique_col_names(self):
        """Set self.is_valid = False if a double column name is found and give an
        error message specifying the duplicate column name(s).
        """
        columns = self.tree_df.columns
        duplicate_columns = set(columns[columns.duplicated()])

        if duplicate_columns:
            self.can_continue = False
            self.is_valid = False
            logger.error(' Detected duplicate column name(s): \n\t' + '\n\t'.join(duplicate_columns))

    def transmart_data_types(self):
        """ Checks whether the column tranSMART data type is not empty and contains the allowed data types.
        """
        for counter, data_type in enumerate(self.tree_df['tranSMART data type'], start=self.n_comment_lines + 1):
            if pd.isnull(data_type) and not pd.isnull(self.tree_df['Column name'][counter]):
                self.is_valid = False
                logger.error(" No data type entered in row {} of column 'tranSMART data type'.".format(counter + 1))
            if data_type not in ['Low-dimensional', 'High-dimensional'] and not pd.isnull(data_type):
                self.is_valid = False
                logger.error(" Wrong data type '{}' in row {} of column 'tranSMART data type'. Only 'Low-dimensional' "
                             "or 'High-dimensional' allowed.".format(data_type, counter + 1))

    def data_source_referenced(self):
        """ Checks whether columns 'Column name' and 'Sheet name/File name' are either both filled out or both empty.
        """
        for i in range(self.n_comment_lines + 1, self.n_comment_lines + 1 + len(self.tree_df)):
            col_name = self.tree_df['Column name'][i]
            sheet_or_file_name = self.tree_df['Sheet name/File name'][i]
            if not pd.isnull(sheet_or_file_name) and pd.isnull(col_name):
                self.is_valid = False
                logger.error(" Row {} contains a 'Sheet name/File name', but no 'Column name' is given.".format(i + 1))
            if pd.isnull(sheet_or_file_name) and not pd.isnull(col_name):
                self.is_valid = False
                logger.error(" Row {} contains a 'Column name' which is not referenced in "
                             "'Sheet name/File name'.".format(i + 1))

    def consecutive_levels(self):
        """ Checks whether the levels that are present are consecutive.
        """
        level_nums = []

        for col in self.tree_df.columns:
            try:
                level_nums.append(int(col[-1:]))
            except ValueError:
                pass

        for counter, num in enumerate(level_nums, 1):
            if num != counter:
                logger.error(' Level numbers should be consecutive, starting to count from 1 (e.g. Level 1, Level 2, '
                             'Level 3... etc.')

    def check_level_1(self):
        """ Checks whether column 'Level 1' contains one unique entry.
        """
        if len(self.tree_df['Level 1'].dropna().unique()) != 1:
            logger.error(" Column 'Level 1' contains no entry or more than one unique entry.")
