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
                              self.check_data_source,
                              ])

        self.validate_sheet()

    def value_substitution_unique(self):
        """ Checks whether the combination of Sheet name/File name and Column name is unique.
        """
        self.df['Combo'] = tuple(zip(self.df['Sheet name/File name'], self.df['Column name'], self.df['From value']))

        unique = []
        for counter, combo in enumerate(self.df['Combo'], start=self.n_comment_lines + 1):
            if combo in unique:
                self.is_valid = False
                self.logger.error(" Row {} contains a duplicate value substitution.".format(counter + 1))
            else:
                unique.append(combo)

    def check_data_source(self):
        """ Checks whether data source referenced in 'Sheet name/File name' is filled out and present in source_dir.
        """
        files_no_ext = [".".join(file.split(".")[:-1]) for file in os.listdir(self.source_dir)]

        for counter, data_source in enumerate(self.df['Sheet name/File name'], start=self.n_comment_lines + 1):
            if pd.isnull(data_source):
                self.is_valid = False
                self.can_continue = False
                self.logger.error(" No data source referenced at row {} in column 'Sheet name/File name'"
                                  .format(counter + 1))
            else:
                if data_source.rsplit('.')[0] not in self.template.sheet_names and data_source.rsplit('.')[0] not in \
                        files_no_ext:
                    self.is_valid = False
                    self.can_continue = False
                    self.logger.error(" Clinical data in sheet or file '{}' not found. Check whether it is correctly "
                                      "referenced in column 'Sheet name/File name and is a sheet in the template or a "
                                      "file stored in the same directory as the template."
                                      .format(data_source.rsplit('.')[0]))
