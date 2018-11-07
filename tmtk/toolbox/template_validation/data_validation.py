import logging

logger = logging.getLogger("Clinical data ")


class DataValidator:

    def __init__(self, data_df, tree_df):
        """Creates object DataValidator that runs validation tests on clinical data and gives user-friendly
        error messages.

        :param self.data_df: clinical data in pandas data frame
        :param self.end_comments: stores index of first line in data sheet that is not a comment
        :param self.can_continue: boolean tracking if data passes validation steps
        :param self.tests_to_run: dict containing function calls for data validation tests
        """
        self.data_df = data_df
        self.tree_df = tree_df
        self.end_comments = 0
        self.can_continue = True
        self.tests_to_run = {'1': self.after_comments(),
                             '2': self.no_special_characters(),
                             '3': self.mandatory_col(),
                             '4': self.unique_colnames(),
                             '5': self.colname_in_tree_sheet()
                             }

    def after_comments(self):
        """Determines where initial text with comments (instructions for data owner) ends, save data_df without
        these comments to continue checking and assign column names.
        """
        i = 0
        while str(self.data_df.iloc[i, 0]).startswith('#'):
            i += 1

        if i != 0:
            header = self.data_df.iloc[i]
            self.data_df = self.data_df[i + 1:]
            self.data_df = self.data_df.rename(columns=header)
            self.end_comments = i
        else:
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
                    self.can_continue = False
                    logger.error("Detected special character at column: '{}', row: {}.".format(
                        col_name, str(j + 3 + self.end_comments)))

                if '\xa0' in str(self.data_df.iloc[j, i]):
                    self.can_continue = False
                    logger.error("Detected non-breaking space at column: '{}', row: {}. ".format
                                 (col_name, str(j + 3 + self.end_comments)))

                if any((e_t in enter_tab) for e_t in str(self.data_df.iloc[j, i])):
                    self.can_continue = False
                    logger.error("Detected enter or tab at column: '{}', row: {}. ".format
                                 (col_name, str(j + 3 + self.end_comments)))

        # delete '#' from self.data_df so that checking of data can continue
        self.data_df = self.data_df.replace('#', '', regex=True)

    def mandatory_col(self):
        """Set self.can_continue = False if a subject identifier column called 'SUBJ_ID' is
        not present in the clinical data and give an error message if it is not.
        """
        if 'SUBJ_ID' not in self.data_df.columns:
            self.can_continue = False
            logger.error("Mandatory column containing subject identifiers (SUBJ_ID) not detected "
                         "in clinical data.")

    def unique_colnames(self):
        """Set self.can_continue = False if a double column name is found and give an
        error message specifying the duplicate column name(s).
        """
        col_names = self.data_df.columns.values.tolist()
        single_names = []

        for name in col_names:
            if name not in single_names:
                single_names.append(name)
            else:
                logger.error("Detected duplicate column name: '{}'.".format(name))
                self.can_continue = False

    def colname_in_tree_sheet(self):
        """Set self.can_continue = False if a column name in clinical data and tree structure
        sheet do not match. Give an error message specifying which column name(s) do not match.

        :param tree_sheet_columns: list of entries in Tree structure sheet, Column name
        :param data_columns: list of column names in clinical data
        """
        data_columns = self.data_df.columns.values.tolist()

        for col in data_columns:
            if col != 'SUBJ_ID':
                if col not in self.tree_df['Column name'].values.tolist():
                    logger.error("Column name: '{}' not listed in Tree structure column: 'Column name'.".format(col))
                    self.can_continue = False
