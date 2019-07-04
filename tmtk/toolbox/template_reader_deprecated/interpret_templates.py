import os
import re
from collections import defaultdict

import numpy as np
import pandas as pd

from . import template_validation as Validity
from .template_data import TemplatedStudy, HighDim


def get_clinical_template(study):
    """Try to detect the clinical template file in the source dir and open it with pandas."""
    clinical_templates = [template for template in study.excel_files if "clin" in template.lower() and
                          "~$" not in template]

    clinical_template = None
    if len(clinical_templates) == 1:
        clinical_template_name = clinical_templates[0]
        clinical_template = pd.ExcelFile(clinical_template_name)
        print("[INFO] Clinical data template detected: " + clinical_template_name)
    elif len(clinical_templates) == 0:
        study.clinical_template_present = False
        print("[WARNING] No clinical data template could be detected. Assuming only high-dimensional templates " +
              "are available.")
    else:
        print("[ERROR] Too many clinical data templates were found. " +
              "Make sure only one file has 'clinical' in its name.")
        Validity.list_length(clinical_templates, expected=1)

    return clinical_template


def get_sheet_dict(workbook, comment_char="#"):
    """Return a sheet dictionary of all sheets in the workbook."""
    sheets = {sheet_name: workbook.parse(sheet_name, comment=comment_char, dtype='object')
              for sheet_name in workbook.sheet_names}
    return sheets


def get_tree_sheet(sheets):
    """Detect the name of sheet in the clinical template that contains the tree structure."""

    tree_sheets = [sheet for sheet in sheets if "tree" in sheet.lower() and "example" not in sheet.lower()]
    Validity.list_length(tree_sheets, expected=1)
    tree_sheet_name = tree_sheets[0]

    return tree_sheet_name


def get_data_file_name(data_file, sheets, data_type="Low-dimensional"):
    """Return the clinical data file name with extension if it is present in one of the sheets."""
    if data_type == "Low-dimensional" and data_file in sheets.keys():
        data_file += ".tsv"
    return data_file


def construct_concept_cd(row, previous_row, study):
    """Construct concept_cd based on current row in the tree sheet (and info gathered from previous rows)"""
    # Use only colums containing the concept code values
    row = row[3::3].copy()

    # Only for the first row to instantiate concept_cd
    if previous_row is None:
        concept_cd = row
        # Get name of the study from first tree row
        if not study.name:
            study.name = concept_cd["Level 1"]

    # If the new row doesn't contain concept_cd info, keep the concept_cd as it was
    elif not row.any():
        concept_cd = previous_row
        
    # Incorporate the new concept_cd info into what was already known from the previous row(s)
    else:
        new_values = row[row.first_valid_index():]
        # Find the highest node that is different from the previous concept path
        new_col_names = [col for col, value in new_values.iteritems() if value != previous_row[col] and
                         not pd.isnull(value)]
        # Replace values in the previous concept code with those from the new row
        if new_col_names:
            first_new_col_name = new_col_names[0]
            previous_row[first_new_col_name:] = new_values[first_new_col_name:]
        # To do: build check that makes sure there are no nan values in newly created concept_cd
        concept_cd = previous_row

    return concept_cd


def create_concept_cd(concept_cd_series, join_char="+", exclude_study_level=True):
    """Turn the pandas series object into a concept_cd string."""
    concept_cd_series = concept_cd_series.dropna()
    if exclude_study_level:
        concept_cd_series = concept_cd_series[1:]
    concept_code = join_char.join(concept_cd_series)
    return concept_code


def split_concept_cd(concept_cd, join_char="+"):
    """Split up the full concept path into a category_cd and a data label."""
    category_code, data_label = concept_cd.rsplit(join_char, 1)
    return (category_code, data_label)


def subjects_in_tree(study, sheets):
    """Check if the subjects are present in the tree structure template"""
    tree_sheet = sheets[study.tree_sheet_name]
    column_numbers = tree_sheet["Column number"]
    subjects_in_tree = 1 in column_numbers.tolist()
    return subjects_in_tree


def add_subjects_to_mapping(study, sheets):
    """Add a line to the column mapping that links to the subjects for each data file."""
    tree_sheet = sheets[study.tree_sheet_name]
    data_files = tree_sheet[tree_sheet["tranSMART data type"] == "Low-dimensional"]["Sheet name/File name"]
    data_files = data_files.dropna().unique()
    for data_file in data_files:
        data_file_name = get_data_file_name(data_file, sheets, "Low-dimensional")
        study.col_map_rows.add((data_file_name, "", 1, "SUBJ_ID", "", "", ""))


def reformat_concept_path(concept_cd_series):
    """Reformat the concept cd series to the metadata format expected by tm-batch."""
    # Study name is not used in metadata concept path
    if len(concept_cd_series) == 1:
        concept_path = "\\"
    else:
        concept_path = "\\" + "\\".join(concept_cd_series[1:])
    return concept_path


def create_metadata(row, concept_cd_series, index_counter, study):
    """Iterate through metadata in the tree sheet and store in study instance."""
    tags = row[4::3]
    values = row[5::3]

    for index, (tag, value) in enumerate(zip(tags, values)):
        if not pd.isnull(tag):
            matching_concept_cd_series = concept_cd_series[:index + 1]
            concept_path = reformat_concept_path(matching_concept_cd_series)
            index_counter[concept_path] += 100
            study.all_metadata.add((concept_path, tag, value, index_counter[concept_path]))


def write_study_params(study):
    with open(os.path.join(study.output_dir, "study.params"), "w") as study_params_file:
        study_params_file.write("STUDY_ID=" + study.ID + "\n")
        study_params_file.write("SECURITY_REQUIRED=" + study.sec_req + "\n")
        if study.ID != study.name:
            root_dir = "\\Private Studies\\" if study.sec_req == "Y" else "\\Public Studies\\"
            study_params_file.write("TOP_NODE=" + root_dir + study.name + "\n")


def write_clinical_params(study):
    with open(os.path.join(study.clin_output_dir, "clinical.params"), "w") as clin_params_file:
        clin_params_file.write("COLUMN_MAP_FILE=" + study.col_map_file_name + "\n")
        if study.word_map_rows:
            clin_params_file.write("WORD_MAP_FILE=" + study.word_map_file_name + "\n")


def write_metadata_params(study):
    if study.all_metadata:
        with open(os.path.join(study.metadata_output_dir, "tags.params"), "w") as metadata_params_file:
            metadata_params_file.write("TAGS_FILE=" + study.metadata_file_name + "\n")


def get_output_dir(study, hd_template_file_name):
    """Construct HD folder name based on template file name and create the folder."""
    hd_template_file_name = os.path.basename(hd_template_file_name)
    hd_output_dir = os.path.splitext(hd_template_file_name)[0]
    hd_output_dir = re.sub("template", "", hd_output_dir, flags=re.I)
    hd_output_dir = "_".join(hd_output_dir.split())
    hd_output_dir = os.path.join(study.output_dir, hd_output_dir)
    os.makedirs(os.path.join(hd_output_dir, "annotation"), exist_ok=True)
    return hd_output_dir


def get_template_type(experiment):
    """Check type of template by reading the description in the metadata and store template-specific info."""
    description = experiment.sheets.metadata_samples.columns[0].lower()

    if "proteomics" in description:
        experiment.hd_type = "Proteomics"
        experiment.annotation_params_name = "proteomics_annotation.params"
        experiment.hd_data_params_name = "proteomics.params"
    elif all(word in description for word in ("rna expression", "microarray")):
        experiment.hd_type = "RNA_Microarray"
        experiment.annotation_params_name = "mrna_annotation.params"
        experiment.hd_data_params_name = "expression.params"
    elif all(word in description for word in ("copy number", "microarray")):
        experiment.hd_type = "aCGH"
        experiment.annotation_params_name = "cnv_annotation.params"
        experiment.hd_data_params_name = "cnv.params"
    elif all(word in description for word in ("copy number", "genome sequencing")):
        experiment.hd_type = "CNA_DNA-Seq"
        experiment.annotation_params_name = "cnv_annotation.params"
        experiment.hd_data_params_name = "cnv.params"
    elif "rna-seq" in description:
        experiment.hd_type = "RNA-Seq"
        experiment.annotation_params_name = "rnaseq_annotation.params"
        experiment.hd_data_params_name = "rnaseq.params"
    else:
        raise Validity.TemplateException("Could not detect template type from description in first row:\n" +
                                         description)


def get_row_section(df, start_value=None, end_value=None):
    """Return a section of rows from a df, based on the start and/or end value to be found in the first column."""
    if start_value:
        first_row_index = df.loc[df.iloc[:, 0] == start_value].index[0]
    else:
        first_row_index = 0
    if end_value:
        last_row_index = df.loc[df.iloc[:, 0] == end_value].index[0]
    else:
        last_row_index = len(df.index)

    section = df.iloc[first_row_index:last_row_index + 1, :]
    return section


def process_human_names(names_list):
    """Return a single formatted string as metadata value."""
    value = ", ".join(names_list)
    return value


def extract_hd_metadata(study, experiment, concept_cd):
    """Extract the general info and protocols section from HD metadata sheet and store in metadata object."""
    metadata_concept_cd = "\\" + concept_cd.replace("+", "\\")
    sheet = experiment.sheets.metadata_samples

    general_info = get_row_section(sheet, "Description", "Related publication DOI link")
    protocols = get_row_section(sheet, "Sample processing, descriptive", "Value definition")

    tag_index = 10
    for section in (general_info, protocols):
        for index, row in section.iterrows():

            row = row.dropna().tolist()
            tag = row[0]
            # Metadata fields left empty by data provider will not be inserted
            if len(row) == 1:
                continue
            elif tag in ('Submitter name(s)', 'Data owner/PI name'):
                value = process_human_names(row[1:])
            elif Validity.list_length(row[1:], expected=1):
                value = row[1]
            if tag == "Genome build":
                experiment.genome_build = value
            metadata_row = (metadata_concept_cd, tag, value, tag_index)
            study.all_metadata.add(metadata_row)
            tag_index += 1

    # Additionally add the platform ID derived from the ss-mapping to the standardized metadata
    study.all_metadata.add((metadata_concept_cd, "Platform ID", experiment.platform_id, tag_index))
    # Add platform name and ID to the high-dim directory level
    concept_cd_dir_level = metadata_concept_cd.rsplit("\\", 1)[0]
    study.add_dir_level_metadata(concept_cd_dir_level, experiment.platform_id, experiment.platform_name)


def retrieve_ss_df(experiment):
    """Retrieve the subject sample data as provided in the template as a separate re-indexed df."""
    sheet = experiment.sheets.metadata_samples
    ss_data = get_row_section(sheet, "Subject ID")
    ss_data.columns = ss_data.iloc[0]
    ss_data = ss_data.reset_index(drop=True)
    ss_data = ss_data.drop(ss_data.index[0])
    ss_data = ss_data.reset_index(drop=True)
    Validity.empty_df(ss_data, mandatory=True, df_name="subject-sample mapping", workbook_name=experiment.workbook_name)
    return ss_data


def process_mapping(ss_data, experiment, concept_cd, study):
    """Add required high-dim properties to the experiment instance and combine the ss_data with info from metadata
    to write the subject-sample mapping file."""
    determine_hd_properties(ss_data, experiment)
    cols = ["STUDY_ID", "SITE_ID", "SUBJECT_ID", "SAMPLE_CD", "PLATFORM", "SAMPLE_TYPE", "TISSUE_TYPE",
            "TIME_POINT", "CATEGORY_CD", "SOURCE_CD"]

    ss_mapping = pd.DataFrame(columns=cols)
    ss_mapping["SUBJECT_ID"] = ss_data["Subject ID"]
    ss_mapping["STUDY_ID"] = study.ID
    ss_mapping["SAMPLE_CD"] = ss_data["Sample ID"]
    ss_mapping["PLATFORM"] = ss_data["Platform"]
    ss_mapping["SAMPLE_TYPE"] = ss_data["Sample type"]
    ss_mapping["TISSUE_TYPE"] = ss_data["Tissue type"]
    ss_mapping["TIME_POINT"] = ss_data["Timepoint"]
    ss_mapping["CATEGORY_CD"] = concept_cd
    ss_mapping["SOURCE_CD"] = ""

    write_hd_df(ss_mapping, experiment.output_dir, "subject_sample_mapping.tsv")


def write_hd_df(df, hd_output_dir, file_name, subdir=""):
    """Write a high-dim df to the desired location."""
    full_hd_output_dir = os.path.join(hd_output_dir, subdir)
    os.makedirs(full_hd_output_dir, exist_ok=True)
    output_file_path = os.path.join(full_hd_output_dir, file_name)
    df.to_csv(output_file_path, sep="\t", index=False, na_rep="")


def determine_hd_properties(ss_data, experiment):
    """Validate the ss-mapping columns and save the info needed for the params files in the HD class instance."""
    uniform_props = {col: ss_data[col] for col in ["Platform", "Platform name", "Organism"]}
    unique_props = {col: ss_data[col] for col in ["Sample ID"]}
    Validity.check_uniformity(uniform_props.values())
    Validity.check_uniqueness(unique_props.values())
    experiment.organism = uniform_props["Organism"][0]
    experiment.platform_id = uniform_props["Platform"][0]
    experiment.platform_name = uniform_props["Platform name"][0]


def process_platform(experiment):
    """To each type of platform add the required columns and send the result to the write function."""
    platform_sheet = experiment.sheets.platform
    if experiment.hd_type == "RNA_Microarray":
        platform_sheet.insert(0, "GPL_ID", experiment.platform_id)
        platform_sheet["ORGANISM"] = experiment.organism
    elif experiment.hd_type == "Proteomics":
        platform_sheet.insert(2, "ORGANISM", experiment.organism)
        platform_sheet.insert(3, "GPL_ID", experiment.platform_id)
    elif experiment.hd_type in ["aCGH", "CNA_DNA-Seq"]:
        if not {"GENE_SYMBOL", "GENE_ID"}.issubset(set(platform_sheet.columns)):
            platform_sheet["GENE_SYMBOL"] = np.nan
            platform_sheet["GENE_ID"] = np.nan
        platform_sheet.insert(0, "GPL_ID", experiment.platform_id)
        platform_sheet["ORGANISM"] = experiment.organism
        if experiment.hd_type == "CNA_DNA-Seq":
            platform_sheet.insert(5, "NUM_PROBES", np.nan)
    elif experiment.hd_type == "RNA-Seq":
        platform_sheet.insert(0, "GPL_ID", experiment.platform_id)
        platform_sheet.insert(5, "NUM_PROBES", np.nan)
        platform_sheet["ORGANISM"] = experiment.organism

    write_hd_df(platform_sheet, experiment.output_dir, experiment.platform_id + ".tsv", "annotation")


def process_hd_data(experiment):
    """Send the df from the data sheet to the write function."""
    data_sheet = experiment.sheets.data
    output_file_name = experiment.hd_type + "_data.tsv"

    if experiment.hd_type in ["aCGH", "CNA_DNA-Seq"]:
        data_sheet = edit_header(data_sheet)

    write_hd_df(data_sheet, experiment.output_dir, output_file_name)


def edit_header(data_sheet):
    """Replace the columns name suffixes for CNA data df's'"""
    old_cols = data_sheet.columns
    new_cols = [col.replace('.call', '.flag') if col.endswith('.call') else
                col.replace('.ratio', '.chip') if col.endswith('.ratio') else
                col for col in old_cols]
    data_sheet.columns = new_cols
    return data_sheet


def write_platform_params(experiment):
    """Write HD annotations params file."""
    params_output_path = os.path.join(experiment.output_dir, "annotation", experiment.annotation_params_name)

    with open(params_output_path, "w") as annotation_params_file:
        if experiment.platform_id:
            annotation_params_file.write("PLATFORM=" + experiment.platform_id + "\n")
            annotation_params_file.write("ANNOTATIONS_FILE=" + experiment.platform_id + ".tsv" + "\n")
        if experiment.platform_name:
            annotation_params_file.write("TITLE=" + experiment.platform_name + "\n")
        if experiment.organism:
            annotation_params_file.write("ORGANISM=" + experiment.organism + "\n")
        if experiment.genome_build:
            annotation_params_file.write("GENOME_RELEASE=" + experiment.genome_build + "\n")


def write_hd_data_params(experiment):
    """Write HD data params file."""
    params_output_path = os.path.join(experiment.output_dir, experiment.hd_data_params_name)

    with open(params_output_path, "w") as hd_data_params_file:
        if experiment.hd_type:
            hd_data_params_file.write("DATA_FILE=" + experiment.hd_type + "_data.tsv" + "\n")
        hd_data_params_file.write("DATA_TYPE=" + "R" + "\n")
        # hd_data_params_file.write("LOG_BASE="+"2"+"\n")
        hd_data_params_file.write("MAP_FILENAME=" + "subject_sample_mapping.tsv" + "\n")
        # hd_data_params_file.write("ALLOW_MISSING_ANNOTATIONS=" + "N" + "\n")
        # hd_data_params_file.write("SKIP_UNMAPPED_DATA=" + "N" + "\n")
        # hd_data_params_file.write("ZERO_MEANS_NO_INFO=" + "N" + "\n")


def write_clinical_data_sheets(study, sheets):
    """In case the clinical data is in the clinical template sheet(s), write them to txt files"""
    tree_sheet = sheets[study.tree_sheet_name]
    data_files = tree_sheet["Sheet name/File name"].dropna().unique().tolist()
    for file in data_files:
        if file in sheets.keys():
            clinical_data_sheet = sheets[file]
            write_location = os.path.join(study.clin_output_dir, file) + ".tsv"
            clinical_data_sheet.to_csv(write_location, sep="\t", index=False, na_rep="")
            print("[INFO] Clinical data file written at: {0}".format(write_location))


def process_column_mapping(study, sheets):
    """Extract all information required to build the column mapping and write it to the clinical dir."""
    add_subjects_to_mapping(study, sheets)
    if subjects_in_tree(study, sheets):
        pass
        #duplicate_subjects_col()

    previous_concept_cd_series = None
    for index, row in sheets[study.tree_sheet_name].iterrows():
        data_type = row["tranSMART data type"]
        data_file = get_data_file_name(row["Sheet name/File name"], sheets, data_type)
        col_nr = int(row["Column number"]) if not np.isnan(row["Column number"]) else None
        concept_cd_series = construct_concept_cd(row, previous_concept_cd_series, study)
        concept_code = create_concept_cd(concept_cd_series, "+")

        if data_type == "Low-dimensional" and col_nr:
            category_code, data_label = split_concept_cd(concept_code)
            col_map_row = (data_file, category_code, col_nr, data_label, "", "", "")
            study.col_map_rows.add(col_map_row)

        elif data_type == "High-dimensional":
            study.hd_dict[data_file] = concept_code
        previous_concept_cd_series = concept_cd_series

    study.write_column_mapping()


def process_word_mapping(study, sheets):
    """If present, write word mapping rows to file."""
    word_map_sheets = [sheet for sheet in sheets if "value substitution" in sheet.lower()
                       and 'example' not in sheet.lower()]
    Validity.list_length(word_map_sheets, expected=1)
    study.word_map_sheet_name = word_map_sheets[0]
    for index, row in sheets[study.word_map_sheet_name].iterrows():
        word_map_row = tuple(row.tolist())
        study.word_map_rows.add(word_map_row)
    study.write_word_mapping()


def process_clin_metadata(study, sheets):
    """Collect all metadata present in the clinical template."""
    index_counter = defaultdict(int)
    previous_concept_cd_series = None
    for index, row in sheets[study.tree_sheet_name].iterrows():
        concept_cd_series = construct_concept_cd(row, previous_concept_cd_series, study)
        create_metadata(row, concept_cd_series, index_counter, study)
        previous_concept_cd_series = concept_cd_series
    study.write_metadata()


def write_low_dim_params(study):
    """Write all the low-dimensional and study params files."""
    write_study_params(study)
    write_metadata_params(study)
    if study.clinical_template_present:
        write_clinical_params(study)


def process_clinical(study):
    """Get clinical template and call all clinical processing functions."""
    clinical_template = get_clinical_template(study)

    # If present, process general study level metadata template
    process_general_study_metadata(study)

    if study.clinical_template_present:
        sheets = get_sheet_dict(clinical_template)
        study.tree_sheet_name = get_tree_sheet(sheets)

        # Write sheets containing clinical data to .tsv files
        write_clinical_data_sheets(study, sheets)
        # Write column mapping file and collect paths for high-dimensional data
        process_column_mapping(study, sheets)
        # Write word mapping file
        process_word_mapping(study, sheets)
        # Store and write metadata present in tree sheet
        process_clin_metadata(study, sheets)


def process_general_study_metadata(study):
    """Check for general study metadata template and if present write to metadata."""
    study_metadata_template_path = find_general_study_metadata(study)
    if study_metadata_template_path:
        add_general_study_metadata(study, study_metadata_template_path)


def find_general_study_metadata(study):
    """If present return the name of the template containing general study level metadata."""
    # Try to automatically detect which of the template files contains the clinical data
    templates = [template for template in study.excel_files if "general study metadata" in template.lower() and
                 "~$" not in template]
    study_metadata_template_path = None
    if len(templates) == 0:
        print("[WARNING] No general study metadata template could be detected. Make sure the file name contains " +
              "'general study metadata'.")
    elif len(templates) > 1:
        print("[WARNING] Multiple templates detected containing 'general study metadata' in file name. " +
              "Please provide only one. Templates will now be ignored.")
    else:
        study_metadata_template_path = templates[0]
    return study_metadata_template_path


def add_general_study_metadata(study, study_metadata_template_path):
    """Read the data from general study level metadata template and write to tags file."""
    metadata = pd.ExcelFile(study_metadata_template_path, comment="#")

    if len(metadata.sheet_names) > 1:
        print("[WARNING] Multiple sheets detected in general study metadata template. Assuming first sheet.")
    df = metadata.parse(0, header=None)
    tag_index = 10
    for __, row in df.iterrows():
        data = row[row.first_valid_index():].dropna().tolist()
        if len(data) == 2:
            tag = data[0]
            value = data[1]
            study.all_metadata.add(("\\", tag, value, tag_index))
            tag_index += 1
    study.write_metadata()


def collect_high_dim_templates(study):
    """Add the high-dim template files to the dictionary in case these are not specified in a clinical template."""
    study.hd_dict = {file: "<CONCEPT PATH>" for file in study.excel_files if "clin" not in file.lower() and
                     "general" not in file.lower()}


def process_high_dim(study):
    """Loop through high-dim templates and write all mapping, platform and (meta)data."""
    # Case where there are only high-dimensional data templates
    if not study.hd_dict and not study.clinical_template_present:
        collect_high_dim_templates(study)

    for hd_template, concept_cd in study.hd_dict.items():
        print("\n[INFO] Processing high-dim template: {0}".format(hd_template))
        # General processing
        experiment = HighDim()
        experiment.workbook_name = os.path.basename(hd_template)
        experiment.output_dir = get_output_dir(study, hd_template)

        experiment.read_hd_file_template(study.source_dir, hd_template)

        # Get template specific characteristics from the description in the template header
        get_template_type(experiment)

        # Subject-sample mapping
        ss_data = retrieve_ss_df(experiment)
        process_mapping(ss_data, experiment, concept_cd, study)

        # Metadata
        extract_hd_metadata(study, experiment, concept_cd)

        # Platform
        if experiment.sheets.platform is not None:
            process_platform(experiment)
        write_platform_params(experiment)

        # High-dimensional data
        if experiment.sheets.data is not None:
            process_hd_data(experiment)
        write_hd_data_params(experiment)

        print("[INFO] Completed processing of high-dim template: {0}".format(experiment.workbook_name))

    study.finalize_dir_level_metadata()
    study.write_metadata()


def create_study_from_templates(ID, source_dir, output_dir=None, sec_req="Y"):
    """
    Create tranSMART files in designated output_dir for all data provided in templates in the source_dir.

    :param ID: study ID.
    :param source_dir: directory containing all the templates.
    :param output_dir: directory where the output should be written.
    :param sec_req: security required? "Y" or "N", default="Y".
    :return: None
    """

    study = TemplatedStudy(ID=ID, source_dir=source_dir, output_dir=output_dir, sec_req=sec_req)

    process_clinical(study)
    write_low_dim_params(study)
    process_high_dim(study)
    print("[INFO] Templates processed successfully!")
    Validity.TemplateException.epilogue(huge_succes=True)
