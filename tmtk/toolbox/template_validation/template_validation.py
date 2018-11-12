import tmtk
import logging
import os
import pandas as pd

from .data_validation import DataValidator
from .tree_sheet_validation import TreeValidator
from .value_substitution_validation import ValueSubstitutionValidator

logger = logging.getLogger("Template validation")
logger.setLevel(logging.DEBUG)

MANDATORY_SHEETS = ['tree structure', 'value substitution']

COMMENT = '#'


def validate(template_filename, source_dir=None):
    """ Validate the structure and data in 16.2 clinical templates.

    :param template_filename: Template Excel file to parse
    :param source_dir: directory containing all the templates (currently not used).
    """
    if not tmtk.options.transmart_batch_mode:
        logger.fatal('Only 16.2 templates can be validated. Make sure you are loading a 16.2 template and before '
                     'loading you use the command: tmtk.options.transmart_batch_mode = True.')
    else:
        template_file = os.path.abspath(template_filename)
        if source_dir:
            source_dir = os.path.abspath(source_dir)
        else:
            source_dir = os.path.dirname(template_file)

        template = pd.ExcelFile(template_file, comment=None)
        # TODO: Check if file is a valid file
        # TODO: Check if file is Excel

        # check whether mandatory sheets are present
        sheet_names = [sheet.lower() for sheet in template.sheet_names]
        if not set(MANDATORY_SHEETS).issubset(sheet_names):
            logger.error('Missing mandatory sheet(s). Your file contains the following sheet names:'
                         '\n\t'+'\n\t'.join(template.sheet_names))

        for sheet in template.sheet_names:
            if sheet.lower() == 'tree structure':
                tree_df = template.parse(sheet, comment=COMMENT)
                data_sources = set(tree_df.iloc[:, 1].tolist())
                tree_sheet_validator = TreeValidator(tree_df)
                if tree_sheet_validator.is_valid:
                    logger.info('Tree structure sheet seems okay.')
                else:
                    logger.error('Make adjustments to tree structure sheet according to above instructions and '
                                 're-validate template.')

            if sheet.lower() == 'value substitution':
                value_substitution_df = template.parse('Value substitution', comment=COMMENT)
                value_substitution_validator = ValueSubstitutionValidator(value_substitution_df)
                if value_substitution_validator.is_valid:
                    logger.info('Value substitution sheet seems okay.')
                else:
                    logger.error('Make adjustments to value substitution sheet according to above instructions and '
                                 're-validate template.')

        for data_source in data_sources:
            if data_source in template.sheet_names:
                # load data without comments to check for comments within data fields and without first row as header,
                # otherwise duplicate column names in the same sheet are automatically numbered by pandas
                data_df = template.parse(data_source, header=None, comment=None)
                # Validate data source(s) in DataValidator object
                data_validator = DataValidator(data_df, tree_df, data_source)

                if data_validator.is_valid:
                    logger.info('Clinical data in sheet "{}" seems okay.'.format(data_source))
                else:
                    logger.error('Make adjustments to clinical data in sheet "{}" according to above instructions and '
                                 're-validate template.'.format(data_source))

            else:
                # TODO: Look for file in source_dir -> the data source is probably just the file name
                # Notes: possible excel files, tab-separated and comma or semicolon separated files.
                # Assumption if excel file, use first sheet
                # Define list of supported file extensions --> .txt, tsv, csv, xls, xlsx
                # Can use CSV sniffer function in pandas to determine sep type if none excel
                pass
