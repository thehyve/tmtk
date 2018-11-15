import tmtk
import logging
import os
import pandas as pd

from .data_validation import DataValidator
from .tree_sheet_validation import TreeValidator
from .value_substitution_validation import ValueSubstitutionValidator

logger = logging.getLogger(" Template validation")
logger.setLevel(logging.DEBUG)

MANDATORY_SHEETS = ['tree structure', 'value substitution']

COMMENT = '#'


def validate(template_filename, source_dir=None):
    """ Validate the structure and data in 16.2 clinical templates.

    :param template_filename: Template Excel file to parse
    :param source_dir: directory containing all the templates
    """
    if not tmtk.options.transmart_batch_mode:
        logger.fatal(' Only 16.2 templates can be validated. Make sure you are loading a 16.2 template and before '
                     'loading use the command: tmtk.options.transmart_batch_mode = True.')
    else:
        if source_dir is not None:
            template_file = os.path.join(source_dir, template_filename)
        else:
            template_file = os.path.abspath(template_filename)
            source_dir = os.getcwd()

        template = pd.ExcelFile(template_file, comment=None)
        # TODO: Check if file is a valid file
        # TODO: Check if file is Excel

        # check whether mandatory sheets are present
        sheet_names = [sheet.lower() for sheet in template.sheet_names]
        if not set(MANDATORY_SHEETS).issubset(sheet_names):
            logger.error(' Missing mandatory sheet(s). Your file contains the following sheet names:'
                         '\n\t'+'\n\t'.join(template.sheet_names))

        for sheet in template.sheet_names:
            if sheet.lower() == 'tree structure':
                tree_df = template.parse(sheet, comment=COMMENT)
                data_sources = set(tree_df.iloc[:, 1].tolist())
                tree_sheet_validator = TreeValidator(tree_df)
                if tree_sheet_validator.is_valid:
                    logger.info(' Tree structure sheet seems okay.')

            if sheet.lower() == 'value substitution':
                value_substitution_df = template.parse('Value substitution', comment=COMMENT)
                value_substitution_validator = ValueSubstitutionValidator(value_substitution_df)
                if value_substitution_validator.is_valid:
                    logger.info(' Value substitution sheet seems okay.')

        # Search for data source(s) in template sheets or source_dir and count sources that do not pass data validation.
        invalid_data_sources = 0
        for data_source in data_sources:
            data_source_found = False
            # look for data source in template sheets
            if data_source in template.sheet_names:
                data_source_found = True
                # load data without comments to check for comments within data fields and without first row as header,
                # otherwise duplicate column names in the same sheet are automatically numbered by pandas
                data_df = template.parse(data_source, header=None, comment=None)
                invalid_data_sources += validate_data_source(data_df, tree_df, data_source)

            # Search for data source(s) in same directory as template file (source_dir)
            else:
                for file in os.listdir(source_dir):
                    if file.rsplit('.', 1)[0] == data_source:
                        data_source_found = True
                        # Use python sniffer function (engine='python') to determine separator type if file is not excel
                        if file.rsplit('.', 1)[1] == 'csv' or file.rsplit('.', 1)[1] == 'txt' or \
                                file.rsplit('.', 1)[1] == 'tsv':
                            data_df = pd.read_csv(os.path.join(source_dir, file), sep=None, engine='python',
                                                  header=None)
                            invalid_data_sources += validate_data_source(data_df, tree_df, data_source)
                        if file.rsplit('.', 1)[1] == 'xls' or file.rsplit('.', 1)[1] == 'xlsx':
                            data_df = pd.read_excel(os.path.join(source_dir, file), header=None)
                            invalid_data_sources += validate_data_source(data_df, tree_df, data_source)

            if not data_source_found:
                logger.error(' No clinical data file or sheet named "{}" detected. Make sure the sheet or file is '
                             'referenced correctly in the template. If the data is in separate file(s) from the '
                             'template, it should be stored in the same folder as the '
                             'template file.'.format(data_source))

        if not tree_sheet_validator.is_valid or not value_substitution_validator.is_valid or invalid_data_sources != 0:
            logger.error(' Make adjustments to template and possible other input files according to above instructions '
                         'and re-validate template.')


def validate_data_source(data_df, tree_df, data_source) -> int:
    """Validate data source(s) in DataValidator object. Return 0 if data source is valid and 1 if data source
    contains errors.
    """
    data_validator = DataValidator(data_df, tree_df, data_source)

    if data_validator.is_valid:
        logger.info(' Clinical data in sheet or file "{}" seems okay.'.format(data_source))
        return 0

    return 1
