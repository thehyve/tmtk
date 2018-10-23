import logging

logger = logging.getLogger("Clinical data ")


class DataValidator:

    def __init__(self, data_df):
        """Creates object DataValidator that runs validation tests on clinical data and gives user-friendly
        error messages.

        :param self.data_df: clinical data in pandas data frame
        :param self.end_comments: stores index of first line in data sheet that is not a comment
        :param self.can_continue: boolean tracking if data passes validation steps
        :param self.tests_to_run: dict containing function calls for data validation tests
        """
        self.data_df = data_df
        self.end_comments = 0
        self.can_continue = True
        self.tests_to_run = {'1': self.after_comments(),
                             '2': self.no_special_characters()  # ,
                             # '3': self.mandatory_col()
                             # '4': self.unique_colnames()
                             # '5': self.colname_sheetname_combo(),
                             }

    def is_valid(self) -> bool:
        """Calls functions in dict tests_to_run. If one or more tests result in error messages self.can_continue
        will be set to False, otherwise self.can_continue will be True and the clinical data is added to the Study
        object in create_study_from_templates.

        :return self.can_continue
        """
        for i in range(len(self.tests_to_run)):
            self.tests_to_run[str(i+1)]

        return self.can_continue

    def after_comments(self):
        """Determines where initial text with comments (instructions for data owner) ends
        and save data_df in DataValidator object without these comments to continue checking.
        """
        i = 0
        while str(self.data_df.iloc[i, 0]).startswith('#'):
            i += 1
        self.data_df.columns = self.data_df[i:i + 1].values.tolist()
        self.data_df = self.data_df[i + 1:]
        self.end_comments = i

        return self

    def no_special_characters(self):
        """Iterate through data_df and check for special characters within data and give error message with
        the location column name and row number.
        """
        chars = ('#', '+', '>', '<', '*', '&', '^', '%', '\\', 'α', 'β', '—', '–')
        enter_tab = ('\n', '\t')
        for i in range(len(self.data_df.columns)):
            col_name = self.data_df.columns.values[i]

            for j in range(len(self.data_df)):

                if any((c in chars) for c in str(self.data_df.iloc[j, i])):
                    self.can_continue = False
                    logger.error("Detected special character at column: '{}', row: {}.".format(
                        col_name[0], str(j + 3 + self.end_comments)))

                if '\xa0' in str(self.data_df.iloc[j, i]):
                    self.can_continue = False
                    logger.error("Detected non-breaking space at column: '{}', row: {}. ".format
                                 (col_name[0], str(j + 3 + self.end_comments)))

                if any((e_t in enter_tab) for e_t in str(self.data_df.iloc[j, i])):
                    self.can_continue = False
                    logger.error("Detected enter or tab at column: '{}', row: {}. ".format
                                 (col_name[0], str(j + 3 + self.end_comments)))

        # delete '#' from self.data_df so that checking of data can continue
        self.data_df = self.data_df.replace('#', '', regex=True)

        return self
