import os
import pandas as pd

from ..template_reader.create_study_from_templates import get_template_sheets
from .data_validation import DataValidator
from .tree_sheet_validation import TreeValidator
from .value_substitution_validation import ValueSubstitutionValidator

COMMENT = '#'


def validate(template_filename, source_dir=None):

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
    tree_sheet_validator = TreeValidator(tree_df)
    if tree_sheet_validator.is_valid:
        print('Tree structure sheet seems okay.')
    else:
        print('Make adjustments to tree structure sheet according to above instructions and re-validate template.')

    value_substitution_df = template.parse('Value substitution', comment=COMMENT)
    value_substitution_validator = ValueSubstitutionValidator(value_substitution_df)
    if value_substitution_validator.is_valid:
        print('Value substitution sheet seems okay.')
    else:
        print('Make adjustments to value substitution sheet according to above instructions and re-validate template.')

    # TODO: Write class TreeValidator in tree_validation.py
    # TODO: Write class ValueSubstitutionValidator in value_substitution_validation.py
    # TODO: Look for Tree structure sheet and validate using new class TreeValidator
    # TODO: Look for Value substitution sheet and validate using new class ValueSubstitutionValidator
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
            if data_validator.is_valid:
                print('Clinical data seems okay.')
            else:
                print('Make adjustments to clinical data according to above instructions and re-validate template.')

        else:
            # TODO: Look for file in source_dir -> the data source is probably just the file name
            # Notes: possible excel files, tab-separated and comma or semicolon separated files.
            # Assumption if excel file, use first sheet
            # Define list of supported file extensions --> .txt, tsv, csv, xls, xlsx
            # Can use CSV sniffer function in pandas to determine sep type if none excel
            pass
