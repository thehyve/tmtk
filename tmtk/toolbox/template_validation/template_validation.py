import tmtk
import logging
import os
import pandas as pd
import csv
import collections

from .data_validation import DataValidator
from .tree_sheet_validation import TreeValidator
from .value_substitution_validation import ValueSubstitutionValidator

logger = logging.getLogger(' Template validation')
logger.setLevel(logging.DEBUG)

MANDATORY_SHEETS = ['tree structure', 'value substitution']


def validate(template_filename, source_dir=None):

    """ Validate the structure and data in 16.2 clinical templates.
    :param template_filename: Template Excel file name or path to Template Excel file to parse
    :param source_dir: directory containing the template and possible other source files
    """
    # transmart_batch_mode should be True for loading 16.2 templates
    if not tmtk.options.transmart_batch_mode:
        logger.fatal('Only 16.2 templates can be validated. Make sure you are loading a 16.2 template and before '
                     'loading you use the command: tmtk.options.transmart_batch_mode = True.')
    else:
        # if source_dir is given, template_file is in this directory, otherwise a path to the template file is given
        # and source_dir should be the same as this path
        if source_dir:
            template_file = os.path.join(source_dir, template_filename)
        else:
            template_file = template_filename
            source_dir = os.path.dirname(template_filename)

        # read template file
        template = pd.ExcelFile(template_file, comment=None)
        # TODO: Check if file is a valid file
        # TODO: Check if file is Excel

        # check whether mandatory sheets are present
        sheet_names = [sheet.lower() for sheet in template.sheet_names]
        can_continue = mandatory_sheets_present(sheet_names)
        if not can_continue:
            return

        # read tree structure sheet without comments
        for sheet in template.sheet_names:
            if sheet.lower() == 'tree structure':
                tree_df = template.parse(sheet, comment='#')
        # check whether data sources listed in tree structure sheet have unique names
        can_continue = unique_data_sources(tree_df)
        if not can_continue:
            return

        # validate mandatory sheets and data sources
        tree_sheet_valid = validate_tree_sheet(template)
        value_substitution_sheet_valid = validate_value_substitution_sheet(template, tree_df)

        if not tree_sheet_valid:
            logger.error(' Make adjustments to template to fix errors and re-validate.')
        else:
            invalid_data_sources = validate_data_sources(tree_df, template, source_dir)
            if not value_substitution_sheet_valid or invalid_data_sources > 0:
                logger.error(' Make adjustments to template and possible other input files to fix errors '
                             'and re-validate template.')


def mandatory_sheets_present(sheet_names) -> bool:
    """ Checks whether mandatory sheets are present.
    """
    if not set(MANDATORY_SHEETS).issubset(sheet_names):
        missing_sheets = [sheet for sheet in MANDATORY_SHEETS if sheet not in sheet_names]

        logger.error(' Missing mandatory sheet(s). Make adjustments to the template and re-validate. Your file '
                     'does not contain the following sheet names: \n\t' + '\n\t. '.join(missing_sheets))
        return False

    return True


def unique_data_sources(tree_df) -> bool:
    """ Checks whether data sources listed in the tree structure sheet have unique names.
    """
    data_sources = tree_df.iloc[:,1].dropna().unique()
    file_names = [file.rsplit('.', 1)[0] for file in data_sources]
    duplicate_file_names = [item for item, count in collections.Counter(file_names).items() if count > 1]

    if duplicate_file_names:
        logger.error(' Make adjustments to your source data file names and re-validate. Duplicate names for data '
                     'sources detected: \n\t' + '\n\t'.join(duplicate_file_names))
        return False

    return True


def validate_tree_sheet(template) -> bool:
    """ Validate tree structure sheet in TreeValidator.
    """
    tree_sheet_valid = False
    for sheet in template.sheet_names:
        if sheet.lower() == 'tree structure':
            tree_df = template.parse(sheet, comment=None, header=None)
            tree_sheet_validator = TreeValidator(tree_df)
            if tree_sheet_validator.is_valid:
                logger.info(' Tree structure sheet seems okay.')
                tree_sheet_valid = True

    return tree_sheet_valid


def validate_value_substitution_sheet(template, tree_df) -> bool:
    """ Validate value substitution sheet in ValueSubstitutionValidator.
    """
    value_substitution_sheet_valid = False
    for sheet in template.sheet_names:
        if sheet.lower() == 'value substitution':
            value_substitution_df = template.parse(sheet, comment=None, header=None)
            value_substitution_validator = ValueSubstitutionValidator(value_substitution_df, template, tree_df)
            if value_substitution_validator.is_valid:
                logger.info(' Value substitution sheet seems okay.')
                value_substitution_sheet_valid = True

    return value_substitution_sheet_valid


def validate_data_sources(tree_df, template, source_dir) -> int:
    """ Search for data source(s). Return 0 if all data sources are present and valid and >0
    if 1 or more data sources are missing or contain errors.
    """
    invalid_data_sources = 0
    data_sources = set(tree_df['Sheet name/File name'].dropna().unique())

    for data_source in data_sources:
        invalid_data_sources += read_data_source(data_source, template, source_dir, tree_df)

    return invalid_data_sources


def read_data_source(data_source, template, source_dir, tree_df) -> int:
    """ Search for and read data source(s) in template and in files in source_dir.
    """
    source_found = False
    source_error = False

    if data_source in template.sheet_names:
        source_found = True
        # load data without comments to check for comments within data fields and without first row as
        # header, otherwise duplicate column names in same sheet are automatically numbered by pandas.
        data_df = template.parse(data_source, dtype='str', header=None, comment=None)

    for file in os.listdir(source_dir):
        if file == data_source:
            source_found = True
            # read source if Excel file
            if os.path.splitext(os.path.join(source_dir, file))[1] in ['.xls', '.xlsx']:
                data_df = pd.read_excel(os.path.join(source_dir, file), dtype='str', header=None)
            # Use python sniffer function (engine='python') to determine separator type if file is not Excel
            else:
                try:
                    data_df = pd.read_csv(os.path.join(source_dir, file), dtype='str', sep=None, engine='python',
                                          header=None)
                except csv.Error:
                    source_error = True
                    logger.error(" Clinical data file '{}' cannot be read. It may not be a flat text "
                                 "file.".format(file))

    if source_found and not source_error:
        invalid_data_source = validate_data(data_df, tree_df, data_source)
    elif source_error:
        invalid_data_source = 1
    else:
        invalid_data_source = 1
        logger.error(' No clinical data file or sheet named "{}" detected. Make sure the sheet or file is referenced '
                     'correctly in the template. If the data is in separate file(s) from the template, it should be '
                     'stored in the same folder as the template file.'.format(data_source))

    return invalid_data_source


def validate_data(data_df, tree_df, data_source):
    """ Validate data of data_df in DataValidator object.
    """
    invalid_data_source = 0
    data_validator = DataValidator(data_df, tree_df, data_source)
    if data_validator.is_valid:
        logger.info(' Clinical data in sheet or file "{}" seems okay.'.format(data_source))
    else:
        invalid_data_source = 1

    return invalid_data_source
