import logging

logger = logging.getLogger(' Tree structure')
logger.setLevel(logging.DEBUG)


class TreeValidator:

    def __init__(self, tree_df):
        """" Creates object TreeValidator that runs validation tests on tree structure sheet and
        gives user-friendly error messages.

        :param self.tree_df: value substitution sheet in pandas data frame
        :param self.is_valid: boolean tracking if data passes validation steps
        :param self.tests_to_run: dict containing function calls for data validation tests
        """
        self.tree_df = tree_df
        self.is_valid = True
        self.tests_to_run = {}
