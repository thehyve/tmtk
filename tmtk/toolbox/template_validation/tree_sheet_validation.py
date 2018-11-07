import pandas as pd
import logging
import sys

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

EXPECTED_HEADER = ['TRANSMART_DATA_TYPE', 'SHEET_NAME/FILE_NAME', 'COLUMN_NAME']
OPTIONAL_HEADER = ['DATA_TYPE', 'ONTOLOGY_CODE']
DATA_TYPE_VALUES = ['DATE', 'TEXT', 'NUMERICAL', 'CATEGORICAL']


class TreeValidator:

    def __init__(self, tree_sheet):
        self.tree_sheet = tree_sheet
        self.tree_sheet.columns = self.strip_upper_underscore(self.tree_sheet.columns)
        self.can_continue = True
        self.tests_to_run = {'1': self.validate_column_header(),
                             '2': self.check_colname_sheetname_combination()  # ,
                               #
                               # - Datatype
                               # - Sheet name/File name
                               # - Column name
                               # - Level X etc.
                               # - Check for metadata fields
                               # - Check for optional columns: Ontology code, Data type
                               # Check if any fields in the "data" have a # (as it is the comment char print error (ADVANCED CHECK)
                             }


    def validate_column_header(self):
        missing = [col for col in EXPECTED_HEADER if col not in self.tree_sheet.columns]

        if missing:
            logger.error('The following mandatory columns are missing from the tree sheet: {}'.format(missing))
            self.can_continue = False
            return
        logger.info('All mandatory columns are present in the tree sheet')

        # TODO Process LEVEL and OPTIONAL_HEADERS

    def check_colname_sheetname_combination(self):
        # If Sheet name is empty but Column name is not print, raise error and return line numbers
        source_columns = self.tree_sheet[['SHEET_NAME/FILE_NAME', 'COLUMN_NAME']]
        result = source_columns.apply(self.check_source_columns, axis=1)
        if result.any():
            line_numbers = [idx + 1 for idx, value in result.items() if value]  # idx + offset for comment rows?
            logger.error('Missing source sheet or file name for filled in column on lines {}'.format(line_numbers))

    def strip_upper_underscore(self, input_) -> list:
        return [item.strip().upper().replace(' ', '_') for item in input_]

    def check_source_columns(self, item) -> bool:
        if pd.isnull(item['SHEET_NAME/FILE_NAME']) and pd.notnull(item['COLUMN_NAME']):
            return True
        else:
            return False
