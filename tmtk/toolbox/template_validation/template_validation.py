import os
import pandas as pd

from ..template_reader.create_study_from_templates import get_template_sheets
from .data_validation import DataValidator
# from .tree_sheet_validation import TreeSheetValidator

COMMENT = '#'


def validate(template_filename, source_dir = None):

    template_file = os.path.abspath(template_filename)
    if source_dir:
        source_dir = os.path.abspath(source_dir)
    else:
        source_dir = os.path.dirname(template_file)

    template = pd.ExcelFile(template_file, comment=None)
    # TODO: Check if file is a valid file
    # TODO: Check if file is Excel
    sheet_dict = get_template_sheets(template)
    # TODO: Check if mandatory sheets 'Tree structure' and 'Value substitution' are present

    tree_df = template.parse('Tree structure', comment=COMMENT)
    # tree_sheet_validator = TreeSheetValidator(tree_df)
    # if tree_sheet_validator.is_valid():
    #     print('Tree structure sheet seems okay.')

    # TODO: Write class TreeValidator in tree_validation.py
    # TODO: Write class ValueSubstValidator in value_subst_validation.py
    # TODO: Look for Tree structure sheet and validate using new class TreeValidator
    # TODO: Look for Value substitution sheet and validate using new class ValueSubstValidator
    # Validation should result in clear error messages without any stack traces.
    # When possible all validations should run and give all error messages at once.

    for data_source in sheet_dict['tree structure'].data_sources:
        if data_source in template.sheet_names:
            # load data without comments to check for comments within data fields
            # load data without first row as header, otherwise, if there are no comments in the head of the data file,
            # duplicate column names are numbered by pandas
            data_df = template.parse(data_source, header=None, comment=None)
            # Validate data source in DataValidator object
            data_validator = DataValidator(data_df, tree_df)
            if data_validator.can_continue:
                print('Clinical data seems okay.')
            else:
                print('Make adjustments to clinical data according to above instructions and re-validate template. ')

        else:
            # TODO: Look for file in source_dir -> the data source is probably just the file name
            # Notes: possible excel files, tab-separated and comma or semicolon separated files.
            # Assumption if excel file, use first sheet
            # Define list of supported file extensions --> .txt, tsv, csv, xls, xlsx
            # Can use CSV sniffer function in pandas to determine sep type if none excel
            pass
