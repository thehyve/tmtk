import logging

from .validation import Validator


class ValueSubstitutionValidator(Validator):

    def __init__(self, df, source_dir, template):
        """Creates object ValueSubstitutionValidator that runs validation tests on value substitution sheet and
        gives user-friendly error messages.

        :param self.logger: logger to log errors
        :param self.source_dir: directory containing the template and possible other source files
        :param self.template: the loaded template
        :param self.mandatory_columns: mandatory columns for this sheet
        :param self.tests_to_run: list containing function calls for data validation tests
        """
        super().__init__(df)
        self.logger = logging.getLogger(" Value substitution sheet")
        self.source_dir = source_dir
        self.template = template
        self.mandatory_columns = ['Sheet name/File name', 'Column name', 'From value', 'To value']
        self.tests_to_run = (test for test in
                             [self.after_comments,
                              self.check_mandatory_columns,
                              self.check_forbidden_chars,
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
        self.df = self.df.dropna(subset=['Sheet name/File name', 'Column name']).reset_index(drop=True)
        incorrect_source_reference = set()

        for sheet in self.template.sheet_names:
            if sheet.lower() == 'tree structure':
                tree_df = self.template.parse(sheet, comment='#')

        for counter, data_source in enumerate(self.df['Sheet name/File name']):
            data_source = data_source.rsplit('.')[0]
            column = self.df['Column name'][counter]
            tree_columns = tree_df[tree_df['Sheet name/File name'] == data_source]['Column name'].tolist()

            if data_source in tree_df['Sheet name/File name'].values:
                if column not in tree_columns:
                    self.is_valid = False
                    self.logger.error(
                        " Column '{}' in combination with sheet or file named '{}' not found in tree structure. Check "
                        "whether the reference is correct.".format(column, data_source, column))
            else:
                incorrect_source_reference.add(data_source)

        if incorrect_source_reference:
            self.is_valid = False
            self.logger.error(" Sheet or file named '{}' not found in tree structure. Check whether the reference "
                              "is correct.".format(data_source))
