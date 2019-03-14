import logging

from .validation import Validator


class DataValidator(Validator):

    def __init__(self, df, tree_df, data_source):
        """Creates object DataValidator that runs validation tests on clinical data and gives user-friendly
        error messages.

        :param self.tree_df: tree structure in pandas data frame
        :param self.data_source: name of clinical data sheet or file
        :param self.tests_to_run: list containing function calls for data validation tests
        """
        super().__init__(df)
        self.logger = logging.getLogger(' Clinical data')
        self.tree_df = tree_df
        self.data_source = data_source
        self.tests_to_run = (test for test in
                             [self.after_comments,
                              self.check_forbidden_chars,
                              self.check_whitespace,
                              self.check_encoding,
                              self.mandatory_col,
                              self.unique_col_names,
                              self.col_name_in_tree_sheet,
                              self.tree_col_name_in_data
                              ])

        self.validate_sheet()

    def check_encoding(self):
        """Iterate through data_df and check whether data can be encoded in UTF-8 and for # and \ within data.
        When data cannot be encoded or one of these characters is detected set self.is_valid = False and give error
        message with their location column name and row number.
        """

        for col_name, series in self.df.iteritems():
            for idx, value in series.iteritems():
                if not is_utf8(value):
                    self.logger.error(" Value in '{}' at column '{}', row: {} cannot be UTF-8 "
                                      "encoded.".format(self.data_source, col_name, idx + 1))

    def mandatory_col(self):
        """Set self.is_valid = False if a subject identifier column called 'SUBJ_ID' is
        not present in the clinical data and give an error message if it is not.
        """
        if 'SUBJ_ID' not in self.df.columns:
            self.is_valid = False
            self.logger.error(" Mandatory column containing subject identifiers (SUBJ_ID) not detected in "
                              "clinical data '{}'.".format(self.data_source))

    def col_name_in_tree_sheet(self):
        """Check whether all the columns for the current data source are present in the tree sheet.
        If data source contains additional columns: Log a warning message with all those column names.
        """
        # All column names present in the tree sheet for the current data source
        tree_columns = self.tree_df[self.tree_df['Sheet name/File name'] == self.data_source]['Column name'].tolist()

        missing_columns = [col for col in self.df.columns if col != 'SUBJ_ID' and col not in tree_columns]

        if missing_columns:
            self.logger.warning(" The following column(s) in '" + self.data_source +
                                "' are not listed in Tree structure column: 'Column name': "
                                "\n\t" + "\n\t".join(missing_columns))

    def tree_col_name_in_data(self):
        """Check whether all the columns referenced in the tree sheet are present in the data source(s).
        If data source contains additional columns: Log a warning message with all those column names.
        """
        # All column names present in the tree sheet for the current data source
        tree_columns = self.tree_df[self.tree_df['Sheet name/File name'] == self.data_source]['Column name'].tolist()

        missing_columns = [col for col in tree_columns if col not in self.df.columns]

        if missing_columns:
            self.is_valid = False
            self.logger.error(" The following column(s) listed in Tree structure column: 'Column name' are not "
                                "listed in data sheet or file '" + self.data_source + "': \n\t" + "\n\t"
                                .join(missing_columns))


def is_utf8(string):
    try:
        string.encode()
        return True
    except UnicodeDecodeError:
        return False
