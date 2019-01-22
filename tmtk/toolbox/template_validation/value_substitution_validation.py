import logging
import pandas as pd
import os
import csv

from .validation import Validator


class ValueSubstitutionValidator(Validator):

    def __init__(self, df, source_dir, template):
        """Creates object ValueSubstitutionValidator that runs validation tests on value substitution sheet and
        gives user-friendly error messages.

        :param self.source_dir: directory containing the template and possible other source files
        :param self.template: the loaded template
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
                              self.value_substitution_unique,
                              self.no_empty_cells,
                              self.check_source_validity,
                              ])

        self.validate_sheet()

    def value_substitution_unique(self):
        """ Checks whether the combination of the columns 'Sheet name/File name', 'Column name' and 'From value'
        is unique.
        """
        self.df['column_combo'] = tuple(zip(self.df['Sheet name/File name'], self.df['Column name'],
                                            self.df['From value']))
        duplicate_rows = self.df[self.df.duplicated(subset='column_combo', keep=False)]
        duplicate_rows.index += 1

        index_duplicate_rows = [str(idx) for idx in duplicate_rows.index]

        if index_duplicate_rows:
            self.is_valid = False
            self.logger.error(' The following rows contain a duplicate value substitution: \n\t' + '\n\t'
                              .join(index_duplicate_rows))

    def no_empty_cells(self):
        """ Checks whether no cells are left empty.
        """
        for col_name, series in self.df.iteritems():
            for idx, value in series.iteritems():
                if pd.isnull(value):
                    self.is_valid = False
                    self.can_continue = False
                    self.logger.error(" Column '{}', row  '{}' should not be empty".format(col_name, idx + 1))

    def check_source_validity(self):
        """ Checks whether data source referenced in 'Sheet name/File name' is filled out and present in source_dir.
        """
        files = [file for file in os.listdir(self.source_dir)]
        files_no_ext = [".".join(file.split(".")[:-1]) for file in os.listdir(self.source_dir)]

        for counter, data_source in enumerate(self.df['Sheet name/File name'], start=self.n_comment_lines + 1):
            data_source = data_source.rsplit('.')[0]
            column = self.df['Column name'][counter]

            if data_source not in self.template.sheet_names and data_source not in files_no_ext:
                self.is_valid = False
                self.can_continue = False
                self.logger.error(" Clinical data in sheet or file '{}' not found. Check whether the reference in "
                                  "column 'Sheet name/File name' is correct and is a sheet in the template or a file "
                                  "stored in the same directory as the template.".format(data_source))
            else:
                if data_source in self.template.sheet_names:
                    data_df = self.template.parse(data_source, comment='#')
                    column_in_data(self, column, data_df, data_source)
                else:
                    file_idx = files_no_ext.index(data_source)
                    if files[file_idx].rsplit('.')[1] in ['xls', 'xlsx']:
                        data_df = pd.read_excel(os.path.join(self.source_dir, files[file_idx]), comment='#')
                        column_in_data(self, column, data_df, data_source)
                    else:
                        try:
                            data_df = pd.read_csv(os.path.join(self.source_dir, files[file_idx]), dtype='str', sep=None,
                                                  engine='python')
                            column_in_data(self, column, data_df, data_source)
                        except csv.Error:
                            self.logger.error(" Clinical data file '{}' cannot be read. It may not be a flat text file."
                                              .format(files[file_idx]))


def column_in_data(self, column, data_df, data_source):
    """
    """
    if column not in data_df.columns:
        self.is_valid = False
        self.logger.error(" Column: '{}' not found in sheet or file: '{}".format(column, data_source))
