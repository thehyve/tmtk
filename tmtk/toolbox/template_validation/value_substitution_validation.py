import logging

logger = logging.getLogger("Value substitution sheet")
logger.setLevel(logging.DEBUG)


class ValueSubstitutionValidator:

    def __init__(self, value_df):
        """Creates object ValueSubstitutionValidator that runs validation tests on value substitution sheet and
        gives user-friendly error messages.

        :param self.value_substitution_df: value substitution sheet in pandas data frame
        :param self.can_continue: boolean tracking if data passes validation steps
        :param self.tests_to_run: dict containing function calls for data validation tests
        """
        self.value_df = value_df
        self.is_valid = True
        self.tests_to_run = {}
