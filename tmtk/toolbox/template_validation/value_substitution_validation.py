import logging

from .validation import Validator


class ValueSubstitutionValidator(Validator):

    def __init__(self, df, template, tree_df):
        """Creates object ValueSubstitutionValidator that runs validation tests on value substitution sheet and
        gives user-friendly error messages.

        :param self.logger: logger to log errors
        :param self.template: the loaded template
        :param self.mandatory_columns: mandatory columns for this sheet
        :param self.tests_to_run: list containing function calls for data validation tests
        """
        super().__init__(df)
        self.logger = logging.getLogger(" Value substitution sheet")
        self.template = template
        self.tree_df = tree_df
        self.mandatory_columns = ['Sheet name/File name', 'Column name', 'From value', 'To value']
        self.tests_to_run = (test for test in
                             [self.after_comments,
                              self.check_forbidden_chars,
                              self.check_whitespace,
                              self.check_mandatory_columns,
                              self.no_empty_cells,
                              self.value_substitution_unique,
                              self.source_in_tree,
                              ])

        self.validate_sheet()

    def no_empty_cells(self):
        """ Checks whether no cells are left empty.
        """
        empty_cells = self.df[self.df.isnull().any(axis=1)]
        empty_cells.index += 1

        index_empty_cells = [str(idx) for idx in empty_cells.index]

        if index_empty_cells:
            self.is_valid = False
            self.logger.error(' The following row(s) contain empty cells: \n\t' + '\n\t'.join(index_empty_cells))

    def value_substitution_unique(self):
        """ Checks whether the combination of the columns 'Sheet name/File name', 'Column name' and 'From value'
        is unique.
        """
        duplicate_rows = self.df[self.df.duplicated(subset=['Sheet name/File name', 'Column name', 'From value'],
                                                    keep=False)]
        duplicate_rows.index += 1

        index_duplicate_rows = [str(idx) for idx in duplicate_rows.index]
        if index_duplicate_rows:
            self.is_valid = False
            self.logger.error(' The following rows contain a duplicate value substitution: \n\t' + '\n\t'
                              .join(index_duplicate_rows))

    def source_in_tree(self):
        """ Checks whether data source referenced in 'Sheet name/File name' and corresponding column names are present
        in the tree structure sheet.
        """
        df = self.df.dropna(subset=['Sheet name/File name', 'Column name'])
        df = df.drop_duplicates(subset=['Sheet name/File name', 'Column name']).reset_index(drop=True)

        for counter, data_source in enumerate(df['Sheet name/File name']):
            column = df['Column name'][counter]
            if not ((self.tree_df['Sheet name/File name'] == data_source) &
                    (self.tree_df['Column name'] == column)).any():
                self.logger.error(" Column '{}' in combination with sheet or file named '{}' not found in tree "
                                  "structure. Check whether the reference is correct.".format(column, data_source))
