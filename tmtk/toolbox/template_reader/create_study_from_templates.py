import os

import pandas as pd

import tmtk
from .sheet_exceptions import TemplateException
from .sheets import (TreeSheet, ModifierSheet, ValueSubstitutionSheet,
                     TrialVisitSheet, BlueprintFile, OntologyMappingSheet)
from ...study import Study

COMMENT = '#'

# These sheets have a predefined function and wil be recognized as such,
# as long as they are correctly named (case insensitive).
# Any additional sheets will only be parsed if they are mentioned in the
# "sheet name/file name" column of the "Tree structure" sheet.
KEYWORD_SHEETS = {
    'tree structure': TreeSheet,
    'modifier': ModifierSheet,
    'trial visit': TrialVisitSheet,
    'value substitution': ValueSubstitutionSheet,
    'ontology mapping': OntologyMappingSheet
}


def template_reader(template_filename, source_dir=None) -> Study:
    """
    Create tranSMART files in designated output_dir for all data provided in templates in the source_dir.

    The template should contain at least the following sheets (names case insensitive):
    - Tree structure
    - Value substitution
    Additionally, for 17.x templates the following sheets are also required:
    - Modifier
    - Trial visit
    Note: The sheets need to be present, they can be empty

    :param template_filename: Template Excel file to parse
    :param source_dir: directory containing all the templates (currently not used).

    :return: tmtk.Study
    """
    template_file = os.path.abspath(template_filename)
    if source_dir:
        source_dir = os.path.abspath(source_dir)
    else:
        source_dir = os.path.dirname(template_file)

    template = pd.ExcelFile(template_file, comment=COMMENT)
    sheet_dict = get_template_sheets(template)

    # Create the initial blueprint from the tree_sheet and update with the value substitution sheet
    blueprint = BlueprintFile(sheet_dict['tree structure'])
    blueprint.update_blueprint_item(sheet_dict['value substitution'].word_map)

    # Instantiate the study object with metadata
    study = Study()
    study.ensure_metadata()

    # Add clinical data files to the study
    for data_source in sheet_dict['tree structure'].data_sources:
        if data_source in template.sheet_names:
            data_df = template.parse(data_source, comment=COMMENT)
            study.Clinical.add_datafile(filename='{}.txt'.format(data_source), dataframe=data_df)

        else:
            # TODO: Look for file in source_dir -> the data source is probably just the file name
            # Notes: possible excel files, tab-separated and comma or semicolon separated files.
            # Assumption if excel file, use first sheet
            # Define list of supported file extensions --> .txt, tsv, csv, xls, xlsx
            # Can use CSV sniffer function in pandas to determine sep type if none excel
            pass

    # Process 17.x sheets
    if not tmtk.options.transmart_batch_mode:
        # Generate a dict object with modifiers to be added to the blueprint
        sheet_dict['modifier'].set_initial_modifier_blueprint(study.Clinical.Modifiers.df)

        for var_id, var in study.Clinical.all_variables.items():
            if '@' in var.header:
                sheet_dict['modifier'].update_modifier_blueprint(var.header)
        blueprint.update_blueprint(sheet_dict['modifier'].modifier_blueprint)

        study.Clinical.Modifiers.df = study.Clinical.Modifiers.df.append(sheet_dict['modifier'].df)
        study.Clinical.TrialVisits.df = study.Clinical.TrialVisits.df.append(sheet_dict['trial visit'].df)

        # Add ontology mapping if available
        if 'ontology mapping' in sheet_dict:
            ontology_sheet = sheet_dict['ontology mapping']
            ontology_sheet.update_study(study)

    study.apply_blueprint(blueprint.blueprint, omit_missing=True)

    # add metadata tags without using the blueprint
    tags_df = sheet_dict['tree structure'].create_metadata_tags_file()
    study.Tags.df = study.Tags.df.append(tags_df, ignore_index=True)

    return study


def get_template_sheets(template):
    """Return a dictionary with parsed KEYWORD sheets that were found in the template."""
    sheets_lower = {sheet.lower() for sheet in template.sheet_names}
    if not tmtk.options.transmart_batch_mode and not set(KEYWORD_SHEETS).issubset(sheets_lower):
        raise TemplateException('Missing mandatory template sheets.\nExpected {}\nBut found {}'.format(
            list(KEYWORD_SHEETS.keys()), template.sheet_names))

    keyword_sheet_dict = {}
    for sheet in template.sheet_names:
        sheet_lower = sheet.lower()
        if sheet_lower in KEYWORD_SHEETS:
            cls = KEYWORD_SHEETS[sheet_lower]
            keyword_sheet_dict[sheet_lower] = cls(template.parse(sheet, comment=COMMENT))

    return keyword_sheet_dict
