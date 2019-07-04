import logging
import pandas as pd

from .validation import Validator


class TreeValidator(Validator):

    def __init__(self, df):
        """" Creates object TreeValidator that runs validation tests on tree structure sheet and
        gives user-friendly error messages.

        :param self.tests_to_run: list containing function calls for data validation tests
        """
        super().__init__(df)
        self.logger = logging.getLogger(' Tree structure')
        self.mandatory_columns = ['tranSMART data type', 'Sheet name/File name', 'Column name', 'Level 1',
                                  'Level 1 metadata tag', 'Level 1 metadata value']
        self.tests_to_run = (test for test in
                             [self.after_comments,
                              self.check_forbidden_chars,
                              self.check_whitespace,
                              self.get_mandatory_columns,
                              self.check_mandatory_columns,
                              self.unique_col_names,
                              self.transmart_data_types,
                              self.data_source_referenced,
                              self.consecutive_levels,
                              self.check_level_1
                              ])

        self.validate_sheet()

    def get_mandatory_columns(self):
        """ Checks whether mandatory column names are present in the tree structure sheet.
        """
        for i in range(2, len(self.df.columns)):
            metadata_tag = 'Level ' + str(i) + ' metadata tag'
            metadata_value = 'Level ' + str(i) + ' metadata value'
            level = 'Level ' + str(i)

            # check if 'Level' column has corresponding 'metadata tag' and 'metadata value' columns:
            if level in self.df.columns:
                if metadata_tag not in self.df.columns:
                    self.mandatory_columns.append(metadata_tag)
                if 'Level ' + str(i) + ' metadata value' not in self.df.columns:
                    self.mandatory_columns.append(metadata_value)

            # check if 'metadata tag' and 'metadata value' columns have a corresponding 'Level' column:
            if metadata_tag in self.df.columns and metadata_value in self.df.columns:
                if level not in self.df.columns:
                    self.mandatory_columns.append(level)

    def transmart_data_types(self):
        """ Checks whether the column tranSMART data type is not empty and contains the allowed data types.
        """
        for counter, data_type in enumerate(self.df['tranSMART data type'], start=self.n_comment_lines + 1):
            if pd.isnull(data_type) and not pd.isnull(self.df['Column name'][counter]):
                self.is_valid = False
                self.logger.error(" No data type entered in row {} of column 'tranSMART data "
                                  "type'.".format(counter + 1))
            if data_type not in ['Low-dimensional', 'High-dimensional'] and not pd.isnull(data_type):
                self.is_valid = False
                self.logger.error(" Wrong data type '{}' in row {} of column 'tranSMART data type'. Only "
                                  "'Low-dimensional' or 'High-dimensional' allowed.".format(data_type, counter + 1))

    def data_source_referenced(self):
        """ Checks whether columns 'Column name' and 'Sheet name/File name' are either both filled out or both empty.
        """
        for i in range(self.n_comment_lines + 1, self.n_comment_lines + 1 + len(self.df)):
            col_name = self.df['Column name'][i]
            sheet_or_file_name = self.df['Sheet name/File name'][i]
            if not pd.isnull(sheet_or_file_name) and pd.isnull(col_name):
                self.is_valid = False
                self.logger.error(" Row {} contains a 'Sheet name/File name', but no 'Column name' "
                                  "is given.".format(i + 1))
            if pd.isnull(sheet_or_file_name) and not pd.isnull(col_name):
                self.is_valid = False
                self.logger.error(" Row {} contains a 'Column name' which is not referenced in "
                                  "'Sheet name/File name'.".format(i + 1))

    def consecutive_levels(self):
        """ Checks whether the levels that are present are consecutive.
        """
        level_nums = []

        for col in self.df.columns:
            try:
                level_nums.append(int(col[-1:]))
            except ValueError:
                pass

        missing_levels = sorted([level for level in range(1, max(level_nums)+1) if level not in level_nums])
        if missing_levels:
            self.logger.error('Level numbers are not consecutive; missing levels: {}'.format(missing_levels))

    def check_level_1(self):
        """ Checks whether column 'Level 1' contains one unique entry.
        """
        if len(self.df['Level 1'].dropna().unique()) != 1:
            self.logger.error(" Column 'Level 1' contains no entry or more than one unique entry.")
