import os
import pandas as pd

from .sheet_exceptions import TemplateException
from .sheets import (TreeSheet, ModifierSheet, ValueSubstitutionSheet,
                     TrialVisitSheet, BlueprintFile, OntologyMappingSheet)
from ...study import Study

COMMENT = '#'
EXPECTED_SHEETS = {
    'TreeSheet': 'Tree structure',
    'ModifierSheet': 'Modifier',
    'TrialVisitSheet': 'Trial_visit',
    'ValueSubstitutionSheet': 'Value substitution'
}

OPTIONAL_SHEETS = {
    'Ontology mapping': OntologyMappingSheet
}


def template_reader(template_filename, source_dir=None) -> Study:
    """
    Create tranSMART files in designated output_dir for all data provided in templates in the source_dir.

    The template should contain at least the following four sheets (names case insensitive):
    - Tree structure
    - Modifier
    - Trial_visit
    - Value substitution
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
    tree_sheet, modifier_sheet, value_substitution_sheet, trial_visit_sheet = get_template_sheets(template)

    # Create the initial blueprint from the tree_sheet and update with the value substitution sheet
    blueprint = BlueprintFile(tree_sheet)
    blueprint.update_blueprint_item(value_substitution_sheet.word_map)

    # Instantiate the study object with metadata
    study = Study()
    study.ensure_metadata()

    # Add clinical data files to the study
    for data_source in tree_sheet.data_sources:
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

    # Generate a dict object with modifiers to be added to the blueprint
    modifier_sheet.set_initial_modifier_blueprint(study.Clinical.Modifiers.df)

    for var_id, var in study.Clinical.all_variables.items():
        if '@' in var.header:
            modifier_sheet.update_modifier_blueprint(var.header)
    blueprint.update_blueprint(modifier_sheet.modifier_blueprint)

    study.Clinical.Modifiers.df = study.Clinical.Modifiers.df.append(modifier_sheet.df)
    study.Clinical.TrialVisits.df = study.Clinical.TrialVisits.df.append(trial_visit_sheet.df)

    study.apply_blueprint(blueprint.blueprint, omit_missing=True)

    # add metadata tags without using the blueprint
    tags_df = tree_sheet.create_metadata_tags_file()
    study.Tags.df = study.Tags.df.append(
        tags_df,
        ignore_index=True)

    # add optional sheets
    for name, sheet in OPTIONAL_SHEETS.items():
        if name not in template.sheet_names:
            continue

        parsed_sheet = sheet(template.parse(name, comment=COMMENT))
        parsed_sheet.update_study(study)

    return study


def get_template_sheets(template):
    if set(EXPECTED_SHEETS.values()).issubset(template.sheet_names):
        sheets = [(TreeSheet, 'TreeSheet'),
                  (ModifierSheet, 'ModifierSheet'),
                  (ValueSubstitutionSheet, 'ValueSubstitutionSheet'),
                  (TrialVisitSheet, 'TrialVisitSheet')]

        return [cls(template.parse(EXPECTED_SHEETS[sheet_name], comment=COMMENT))
                for cls, sheet_name in sheets]

    else:
        raise TemplateException('Missing mandatory template sheets.\nExpected {}\nBut found {}'.format(
            EXPECTED_SHEETS.values(), template.sheet_names))
