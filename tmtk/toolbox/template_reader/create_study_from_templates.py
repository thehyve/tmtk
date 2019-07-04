from pathlib import Path

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


def template_reader(template_file, source_dir=None) -> Study:
    """
    Create tranSMART files in designated output_dir for all data provided in templates in the source_dir.

    The template should contain at least the following sheets (names case insensitive):
    - Tree structure
    - Value substitution
    Additionally, for 17.x templates the following sheets are also required:
    - Modifier
    - Trial visit
    Note: The sheets need to be present, but they can be empty

    :param template_file: Template Excel file to parse
    :param source_dir: directory containing the templates and source data.

    :return: tmtk.Study
    """
    if source_dir:
        template_file = Path(source_dir).joinpath(template_file)
    else:
        template_file = Path(template_file).resolve()
        source_dir = Path(template_file).parent
    source_dir = Path(source_dir)

    template = pd.ExcelFile(template_file)
    sheet_dict = get_template_sheets(template)

    # Create the initial blueprint from the tree_sheet and update with the value substitution sheet
    blueprint = BlueprintFile(sheet_dict['tree structure'])
    blueprint.update_blueprint_item(sheet_dict['value substitution'].word_map)

    # Instantiate the study object with metadata
    study = Study()
    study.ensure_metadata()

    # Add clinical data files to the study
    source_dir_files = {path.name: path for path in source_dir.glob('*')}
    for data_source in sheet_dict['tree structure'].data_sources:
        if data_source in template.sheet_names:
            data_df = template.parse(data_source, comment=COMMENT)
        else:
            if data_source not in source_dir_files:
                raise TemplateException('Data source "{}" not found in template or source_dir'.format(data_source))
            data_df = _get_external_source_df(source_dir_files[data_source])
        study.Clinical.add_datafile(filename='{}.txt'.format(Path(data_source).stem), dataframe=data_df)

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


def _get_external_source_df(source_file):
    if source_file.suffix in {'.xlsx', '.xls'}:
        data_df = pd.read_excel(source_file, dtype='object', comment=COMMENT)
    else:
        # Assume text file
        data_df = pd.read_csv(source_file, dtype='object', sep=None, engine='python')
    return data_df
