import logging

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
                              ])

        self.validate_sheet()
