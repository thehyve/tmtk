# coding: utf-8

# In[1]:

import os
import re
import csv
import IPython
import numpy as np
import pandas as pd
from glob import glob
from random import randint
from collections import defaultdict


# In[386]:

class TemplatedStudy:
    def __init__(self, ID, source_dir, output_dir="transmart_files", sec_req="Y", name=None):
        self.ID = ID
        self.name = name
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.sec_req = sec_req

        self.metadata_output_dir = os.path.join(self.output_dir, "tags")
        self.clin_output_dir = os.path.join(self.output_dir, "clinical")
        self.col_map_rows = set()
        self.word_map_rows = set()
        self.all_metadata = set()
        self.hd_dict = {}
        self.col_map_file_name = self.ID + "_column_mapping.tsv"
        self.word_map_file_name = self.ID + "_word_mapping.tsv"
        self.metadata_file_name = self.ID + "_tags.tsv"
        self.tree_sheet_name = None
        self.word_map_sheet_name = None
        self.col_map_header = ("Filename", "Category Code", "Column Number", "Data Label", "Data Label Source",
                               "Control Vocab Cd", "Concept Type")
        self.word_map_header = ("Filename", "Column Number", "Datafile Value", "Mapping Value")
        self.metadata_header = ("concept_key", "tag_title", "tag_description", "index")

        os.makedirs(self.clin_output_dir, exist_ok=True)

    def _sort_write(self, data, key1, key2, output_path, header):
        """Sort and write the input data."""
        data_as_list = list(data)
        data_as_list.sort(key=lambda x: (x[key1], x[key2]))

        with open(output_path, "w") as output_file:
            writer = csv.writer(output_file, delimiter='\t', quotechar=None)
            writer.writerow(header)
            writer.writerows(data_as_list)

    def write_column_mapping(self, delete=True):
        """Sort rows on data file and column number, then write the column mapping rows."""
        output_path = os.path.join(self.clin_output_dir, self.col_map_file_name)
        self._sort_write(self.col_map_rows, 0, 2, output_path, self.col_map_header)
        if delete:
            self.col_map_rows = None

    def write_word_mapping(self):
        """Sort rows on data file and column nubmer, then write the word mapping rows."""
        if self.word_map_rows:
            output_path = os.path.join(self.clin_output_dir, self.word_map_file_name)
            self._sort_write(self.word_map_rows, 0, 1, output_path, self.word_map_header)

    def write_metadata(self, delete=True):
        """Sort rows on concept_path and tag index, then write the metadata rows."""
        if self.all_metadata:
            os.makedirs(self.metadata_output_dir, exist_ok=True)
            output_path = os.path.join(self.metadata_output_dir, self.metadata_file_name)
            self._sort_write(self.all_metadata, 0, 3, output_path, self.metadata_header)
            if delete:
                self.all_metadata = None


# In[403]:

class TemplateException(Exception):
    pass


class Validity:
    def __init__(self, validity_object):
        self.validity_object = validity_object

    def string_contains(self, expected):
        pass

    def check_uniformity(self, allow_nan=False):
        for item in self.validity_object:
            if not allow_nan and pd.isnull(item).any():
                raise TemplateException("Mandatory data series '{0}' has missing values: ".format(item.name) +
                                        str(set(item)))
            values = set(item)
            if len(values) != 1:
                raise TemplateException(("Multiple values detected in data series '{0}' expected" +
                                         " to be uniform: ").format(item.name) + str(values))

    def check_uniqueness(self):
        for item in self.validity_object:
            duplicates = item[item.duplicated(keep=False)]
            if len(duplicates) != 0:
                raise TemplateException(("Duplicates detected in data series '{0}' that should be " +
                                         "unique: ").format(item.name) + str(set(duplicates)))

    def list_length(self, expected):
        length = len(self.validity_object)
        correct_length = length == expected
        if not correct_length:
            error_message = "Incorrect list length: {0}, expected: {1}".format(length, expected)
            raise TemplateException(error_message)
        return True

    def check_missing_annotations(self):
        pass


# In[410]:

def get_clin_template(study):
    """Try to detect the clinical template file in the source dir and open it with pandas."""
    all_files = [excel_file for excel_file in glob(study.source_dir + "/*.xls*")]
    # print("\n".join(all_files))
    # Try to automatically detect which of the template files contains the clinical data
    clinical_templates = [template for template in all_files if "clin" in template.lower() and not "~$" in template]

    # Validity(clinical_templates).list_length(1)
    if len(clinical_templates) == 1:
        clinical_template_name = clinical_templates[0]
        print ("Clinical data template detected: " + clinical_template_name)
    else:
        clinical_template_name = "No template selected"
        print(("The clinical data template could not be detected automatically.\nPlease be a good chap and" +
               " name your files properly."))

    clin_template = all_files[4]
    clin_template = pd.ExcelFile(clin_template, comment="#")
    return clin_template


# In[414]:

def get_sheet_dict(workbook, comment_char="#"):
    """Return a sheet dictionary of all sheets in the workbook."""
    sheets = {sheet_name: workbook.parse(sheet_name, comment=comment_char) for sheet_name in workbook.sheet_names}
    return sheets


# In[415]:

def get_tree_sheet(sheets):
    """Detect the name of sheet in the clinical template that contains the tree structure."""
    # sheets = get_sheet_dict(clin_template)

    # tree_sheets = [sheet for sheet in sheets if "tree" in sheet.lower() and not "example" in sheet]
    # Validity(tree_sheets).list_length(1)
    # tree_sheet_name = tree_sheets[0]

    tree_sheet_name = "Tree structure (example)"
    return tree_sheet_name


# ## Process tree structure sheet

# ### Write sheets containing clinical data to .tsv files

# ### Write column mapping file and collect paths for high-dimensional data

# In[95]:

def get_data_file_name(data_file, sheets, data_type="Low-dimensional"):
    """Return the clinical data file name with extension if it is present in one of the sheets."""
    if data_type == "Low-dimensional" and data_file in sheets.keys():
        data_file += ".tsv"
    return data_file


# In[81]:

def construct_concept_cd(row, previous_row, study):
    """Construct concept_cd based on current row in the tree sheet (and info gathered from previous rows)"""
    # Use only colums containing the concept code values
    row = row[3::3]

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
        first_col_name = new_values.keys()[0]
        # Replace values in the previous concept code with those from the new row
        previous_row[first_col_name:] = new_values
        concept_cd = previous_row

    return concept_cd


# In[412]:

def create_concept_cd(concept_cd_series, join_char="+", exclude_study_level=True):
    """Turn the pandas series object into a concept_cd string."""
    concept_cd_series = concept_cd_series.dropna()
    if exclude_study_level:
        concept_cd_series = concept_cd_series[1:]
    concept_code = join_char.join(concept_cd_series)
    return concept_code


# In[115]:

def split_concept_cd(concept_cd, join_char="+"):
    """Split up the full concept path into a category_cd and a data label."""
    category_code, data_label = concept_cd.rsplit(join_char, 1)
    return (category_code, data_label)


# In[84]:

def subjects_in_tree(study, sheets):
    """Check if the subjects are present in the tree structure template"""
    tree_sheet = sheets[study.tree_sheet_name]
    column_numbers = tree_sheet["Column number (starting from 1)"]
    subjects_in_tree = 1 in column_numbers.tolist()
    return subjects_in_tree


# In[413]:

def add_subjects_to_mapping(study, sheets):
    """Add a line to the column mapping that links to the subjects for each data file."""
    tree_sheet = sheets[study.tree_sheet_name]
    data_files = tree_sheet[tree_sheet["tranSMART data type"] == "Low-dimensional"]["Sheet name/File name"]
    data_files = data_files.dropna().unique()
    for data_file in data_files:
        data_file_name = get_data_file_name(data_file, sheets, "Low-dimensional")
        study.col_map_rows.add((data_file_name, "", 1, "SUBJ_ID", "", "", ""))


# In[86]:

def write_column_mapping(col_map_writer):
    """Sort and write the column mapping rows."""
    col_map_rows_list = list(col_map_rows)
    # Sort column mapping on data file name and secondly on column number.
    col_map_rows_list.sort(key=lambda x: (x[0], x[2]))
    col_map_writer.writerows(col_map_rows_list)


# In[87]:

def duplicate_subjects_col():
    pass


# ### Write word mapping file

# ### Write metadata file

# In[143]:

def reformat_concept_path(concept_cd_series):
    # Study name is not used in metadata concept path
    if len(concept_cd_series) == 1:
        concept_path = "\\"
    else:
        concept_path = "\\" + "\\".join(concept_cd_series[1:])
    return concept_path


# In[164]:

def create_metadata(row, concept_cd_series, index_counter, study):
    tags = row[4::3]
    values = row[5::3]

    for index, (tag, value) in enumerate(zip(tags, values)):
        if not pd.isnull(tag):
            matching_concept_cd_series = concept_cd_series[:index + 1]
            concept_path = reformat_concept_path(matching_concept_cd_series)
            index_counter[concept_path] += 100
            study.all_metadata.add((concept_path, tag, value, index_counter[concept_path]))


# ### Write params files

# ##### Study params file

# In[169]:

def write_study_params(study):
    with open(os.path.join(study.output_dir, "study.params"), "w") as study_params_file:
        study_params_file.write("STUDY_ID=" + study.ID + "\n")
        study_params_file.write("SECURITY_REQUIRED=" + study.sec_req + "\n")
        if study.ID != study.name:
            root_dir = "\\Private studies\\" if study.sec_req == "Y" else "\\Public studies\\"
            study_params_file.write("TOP_NODE=" + root_dir + study.name + "\n")


# ##### Clinical params file

# In[398]:

def write_clinical_params(study):
    with open(os.path.join(study.clin_output_dir, "clinical.params"), "w") as clin_params_file:
        clin_params_file.write("COLUMN_MAP_FILE=" + study.col_map_file_name + "\n")
        if study.word_map_rows:
            clin_params_file.write("WORD_MAP_FILE=" + study.word_map_file_name + "\n")


# ##### Metadata params file

# In[397]:

def write_metadata_params(study):
    if study.all_metadata:
        with open(os.path.join(study.metadata_output_dir, "tags.params"), "w") as metadata_params_file:
            metadata_params_file.write("TAGS_FILE=" + study.metadata_file_name + "\n")


# ## Process high-dimensional workbooks

# In[418]:

class HighDim:
    def __init__(self, output_dir=None, hd_type=None, organism=None, platform_id=None, platform_name=None,
                 genome_build=None, annotation_params_name=None, hd_data_params_name=None):
        self.output_dir = output_dir
        self.hd_type = hd_type
        self.organism = organism
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.genome_build = genome_build
        self.annotation_params_name = annotation_params_name
        self.hd_data_params_name = hd_data_params_name

        self.platform_annotation_ids = set()
        self.data_annotation_ids = set()


# In[188]:

def get_output_dir(study, hd_template_file_name):
    hd_output_dir = os.path.splitext(hd_template_file_name)[0]
    hd_output_dir = re.sub("template", "", hd_output_dir, flags=re.I)
    hd_output_dir = "_".join(hd_output_dir.split())
    hd_output_dir = os.path.join(study.output_dir, hd_output_dir)
    return hd_output_dir


# In[189]:

def get_template_type(experiment, hd_template_description):
    """Check type of template by reading the description in the metadata and store template-specific info."""

    description = hd_template_description.lower()

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
        raise TemplateException("Could not detect template type from description in first row:\n" +
                                hd_template_description)


        # In[190]:


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


# In[191]:

def process_human_names(names_list):
    """Iterate through list of names and return a single formatted string as metadata value."""
    # Remove missing part from names
    # final_names = [list(filter(None, name.split(","))) for name  in names_list]
    # merged_names = [",".join(name) for name in final_names]
    # value = ", ".join(merged_names)

    value = ", ".join(names_list)
    return value


# In[417]:

def extract_hd_metadata(sheet, concept_cd, experiment, study):
    """Extract the general info and protocols section from HD metadata sheet and store in metadata object."""
    metadata_concept_cd = "\\" + concept_cd.replace("+", "\\")

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
            elif Validity(row[1:]).list_length(1):
                value = row[1]
            if tag == "Genome build":
                experiment.genome_build = value
            metadata_row = (metadata_concept_cd, tag, value, tag_index)
            study.all_metadata.add(metadata_row)
            tag_index += 1

    # Additionally add the platform ID derived from the ss-mapping to the standardized metadata
    study.all_metadata.add((metadata_concept_cd, "Platform ID", experiment.platform_id, tag_index))
    # Add platform name and ID to the high-dim directory level
    add_dir_level_metadata(metadata_concept_cd, experiment, study)


# In[416]:

def add_dir_level_metadata(metadata_concept_cd, experiment, study):
    """Add platform name and ID to the parent directory containing the high-dim object."""
    concept_cd_dir_level = metadata_concept_cd.rsplit("\\", 1)[0]
    # tag_index = max(num[3] for num in [row for row in all_metadata if row[0] == concept_cd_dir_level]) + 100
    tag_index = 10
    study.all_metadata.add((concept_cd_dir_level, "Platform name", experiment.platform_name, tag_index))
    study.all_metadata.add((concept_cd_dir_level, "Platform ID", experiment.platform_id, tag_index + 1))


# In[194]:

def retrieve_ss_df(sheet):
    """Retrieve the subject sample data as provided in the template as a separate reindexed df."""
    ss_data = get_row_section(sheet, "Subject ID")
    ss_data.columns = ss_data.iloc[0]
    ss_data = ss_data.reset_index(drop=True)
    ss_data = ss_data.drop(ss_data.index[0])
    ss_data = ss_data.reset_index(drop=True)

    return ss_data


# In[238]:

def process_mapping(ss_data, experiment, concept_cd, study):
    """Add required high-dim properties to the experiment instance and combine the ss_data with info from metadata
    to write the subject-sample mapping file."""
    Determine_hd_properties(ss_data, experiment)
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
    ss_mapping["SOURCE_CD"] = "STD" + str(randint(0, 1000000))

    write_hd_df(ss_mapping, experiment.output_dir, "subject_sample_mapping.tsv")


# In[265]:

def write_hd_df(df, hd_output_dir, file_name, subdir=""):
    """Write a high-dim df to the desired location."""
    full_hd_output_dir = os.path.join(hd_output_dir, subdir)
    os.makedirs(full_hd_output_dir, exist_ok=True)
    output_file_path = os.path.join(full_hd_output_dir, file_name)
    df.to_csv(output_file_path, sep="\t", index=False, na_rep="")


# In[266]:

def Determine_hd_properties(ss_data, experiment):
    """Validate the ss-mapping columns and save the info needed for the params files in the HD class instance."""
    uniform_props = {col: ss_data[col] for col in ["Platform", "Platform name", "Organism"]}
    unique_props = {col: ss_data[col] for col in ["Sample ID"]}
    Validity(uniform_props.values()).check_uniformity()
    Validity(unique_props.values()).check_uniqueness()
    experiment.organism = uniform_props["Organism"][0]
    experiment.platform_id = uniform_props["Platform"][0]
    experiment.platform_name = uniform_props["Platform name"][0]


# In[267]:

def read_hd_sheets(hd_template):
    """Check if all the required sheets are present in the high-dim template and return them as separate variables."""
    sheets = hd_template.sheet_names

    metadata_samples_sheets = [sheet for sheet in sheets if "metadata&samples" in sheet.lower()]
    platform_sheets = [sheet for sheet in sheets if "platform" in sheet.lower()]
    data_sheets = [sheet for sheet in sheets if "matrix" in sheet.lower()]

    # Check if each expected sheet is found exactly once
    for sheet in [metadata_samples_sheets, platform_sheets, data_sheets]:
        Validity(sheet).list_length(1)

    metadata_samples_sheet = hd_template.parse(metadata_samples_sheets[0], comment=None)
    platform_sheet = hd_template.parse(platform_sheets[0], comment="#")
    data_sheet = hd_template.parse(data_sheets[0], comment="#")

    return (metadata_samples_sheet, platform_sheet, data_sheet)


# In[425]:

def process_platform(platform_sheet, experiment, validate=True):
    """To each type of platform add the required columns and send the result to the write function."""
    if experiment.hd_type == "RNA_Microarray":
        platform_sheet.insert(0, "GPL_ID", experiment.platform_id)
        platform_sheet["ORGANISM"] = experiment.organism
    elif experiment.hd_type == "Proteomics":
        platform_sheet.insert(2, "ORGANISM", experiment.organism)
        platform_sheet.insert(3, "GPL_ID", experiment.platform_id)
    elif experiment.hd_type in ["aCGH", "CNA_DNA-Seq"]:
        if not set(["GENE_SYMBOL", "GENE_ID"]).issubset(set(platform_sheet.columns)):
            platform_sheet["GENE_SYMBOL"] = np.nan
            platform_sheet["GENE_ID"] = np.nan
        platform_sheet.insert(0, "GPL_ID", experiment.platform_id)
        platform_sheet["ORGANISM"] = experiment.organism
        if experiment.hd_type == "CNA_DNA-Seq":
            platform_sheet.insert(5, "NUM_PROBES", np.nan)
    elif experiment.hd_type == "RNA-Seq":
        platform_sheet.insert(0, "GPL_ID", experiment.platform_id)
        platform_sheet["ORGANISM"] = experiment.organism

    # if validate:
    #    experiment.platform_annotation_ids = set([ref_id for ref_id in platform_sheet[0]])

    write_hd_df(platform_sheet, experiment.output_dir, experiment.platform_id + ".tsv", "annotation")


# In[269]:

def process_hd_data(data_sheet, experiment):
    """Send the df from the data sheet to the write function."""
    output_file_name = experiment.hd_type + "_data.tsv"
    write_hd_df(data_sheet, experiment.output_dir, output_file_name)


# In[244]:

def write_platform_params(experiment):
    """Write HD annotations params file."""
    params_output_path = os.path.join(experiment.output_dir, "annotation", experiment.annotation_params_name)

    with open(params_output_path, "w") as annotation_params_file:
        annotation_params_file.write("PLATFORM=" + experiment.platform_id + "\n")
        annotation_params_file.write("TITLE=" + experiment.platform_name + "\n")
        annotation_params_file.write("ANNOTATIONS_FILE=" + experiment.platform_id + ".tsv" + "\n")
        annotation_params_file.write("ORGANISM=" + experiment.organism + "\n")
        if experiment.genome_build:
            annotation_params_file.write("GENOME_RELEASE=" + experiment.genome_build + "\n")


# In[245]:

def write_hd_data_params(experiment):
    """Write HD data params file."""
    params_output_path = os.path.join(experiment.output_dir, experiment.hd_data_params_name)

    with open(params_output_path, "w") as hd_data_params_file:
        hd_data_params_file.write("DATA_FILE=" + experiment.hd_type + "_data.tsv" + "\n")
        hd_data_params_file.write("DATA_TYPE=" + "R" + "\n")
        # hd_data_params_file.write("LOG_BASE="+"2"+"\n")
        hd_data_params_file.write("MAP_FILENAME=" + "subject_sample_mapping.tsv" + "\n")
        hd_data_params_file.write("ALLOW_MISSING_ANNOTATIONS=" + "N" + "\n")
        hd_data_params_file.write("SKIP_UNMAPPED_DATA=" + "N" + "\n")
        hd_data_params_file.write("ZERO_MEANS_NO_INFO=" + "N" + "\n")


# In[248]:

def write_clinical_data_sheets(study, sheets):
    """In case the clinical data is in the clinical template sheet(s), write them to txt files"""
    tree_sheet = sheets[study.tree_sheet_name]
    data_files = tree_sheet["Sheet name/File name"].dropna().unique().tolist()
    for file in data_files:
        if file in sheets.keys():
            clinical_data_sheet = sheets[file]
            write_location = os.path.join(study.clin_output_dir, file) + ".tsv"
            clinical_data_sheet.to_csv(write_location, sep="\t", index=False, na_rep="")


# In[249]:

def process_column_mapping(study, sheets):
    """Extract all information required to build the column mapping and write it to the clinical dir."""
    add_subjects_to_mapping(study, sheets)
    if subjects_in_tree(study, sheets):
        duplicate_subjects_col()

    previous_concept_cd_series = None
    for index, row in sheets[study.tree_sheet_name].iterrows():
        data_type = row["tranSMART data type"]
        data_file = get_data_file_name(row["Sheet name/File name"], sheets, data_type)
        concept_cd_series = construct_concept_cd(row, previous_concept_cd_series, study)
        concept_code = create_concept_cd(concept_cd_series, "+")

        if data_type == "Low-dimensional":
            category_code, data_label = split_concept_cd(concept_code)
            col_nr = int(row["Column number (starting from 1)"])
            col_map_row = (data_file, category_code, col_nr, data_label, "", "", "")
            study.col_map_rows.add(col_map_row)

        elif data_type == "High-dimensional":
            study.hd_dict[data_file] = concept_code
        previous_concept_cd_series = concept_cd_series

    study.write_column_mapping()


# In[250]:

def process_word_mapping(study, sheets):
    """If present, write word mapping rows to file."""
    # word_map_sheets = [sheet for sheet in sheets if "value substitution" in sheet.lower()
    #                  and not 'example' in sheet.lower()]
    # Validity(word_map_sheets).list_length(1)
    # study.word_map_sheet_name = word_map_sheets[0]
    study.word_map_sheet_name = "Value substitution (example)"
    for index, row in sheets[study.word_map_sheet_name].iterrows():
        word_map_row = tuple(row.tolist())
        study.word_map_rows.add(word_map_row)
    study.write_word_mapping()


# In[251]:

def process_clin_metadata(study, sheets):
    """Collect all metadata present in the clinical template."""
    index_counter = defaultdict(int)
    previous_concept_cd_series = None
    for index, row in sheets[study.tree_sheet_name].iterrows():
        concept_cd_series = construct_concept_cd(row, previous_concept_cd_series, study)
        create_metadata(row, concept_cd_series, index_counter, study)
        previous_concept_cd_series = concept_cd_series
    study.write_metadata(delete=False)


# In[252]:

def write_low_dim_params(study):
    """Write all the low-dimensional and study params files."""
    write_study_params(study)
    write_clinical_params(study)
    write_metadata_params(study)


# In[253]:

def process_clinical(study):
    """Get clinical tempalte and call all clinical processing functions."""
    clin_template = get_clin_template(study)
    sheets = get_sheet_dict(clin_template)
    study.tree_sheet_name = get_tree_sheet(sheets)

    # Write sheets containing clinical data to .tsv files
    write_clinical_data_sheets(study, sheets)
    # Write column mapping file and collect paths for high-dimensional data
    process_column_mapping(study, sheets)
    # Write word mapping file
    process_word_mapping(study, sheets)
    # Store and write metadata present in tree sheet
    process_clin_metadata(study, sheets)


# In[420]:

def process_high_dim(study):
    """Loop through high-dim templates and write all mapping, platform and (meta)data."""
    for hd_template, concept_cd in study.hd_dict.items():
        # General processing
        experiment = HighDim()
        experiment.output_dir = get_output_dir(study, hd_template)

        hd_template = pd.ExcelFile(os.path.join(study.source_dir, hd_template), comment="#")
        (metadata_samples_sheet, platform_sheet, data_sheet) = read_hd_sheets(hd_template)

        # Get template specific characteristics from the description in the template header
        get_template_type(experiment, metadata_samples_sheet.columns[0])

        # Subject-sample mapping
        ss_data = retrieve_ss_df(metadata_samples_sheet)
        process_mapping(ss_data, experiment, concept_cd, study)

        # Metadata
        extract_hd_metadata(metadata_samples_sheet, concept_cd, experiment, study)

        # Platform
        process_platform(platform_sheet, experiment)

        # High-dimensional data
        process_hd_data(data_sheet, experiment)

        # Params files
        write_platform_params(experiment)
        write_hd_data_params(experiment)
        print(vars(experiment))

    study.write_metadata()


# In[421]:

def epilogue(huge_success=True):
    (ID, start) = "HKIbIC9H_Kg", 9
    if huge_success:
        (ID, start) = "S9x6GMM4UWw", 0

        IPython.display.display(IPython.display.YouTubeVideo(ID, autoplay=0, width=0, height=0, start=start))


# In[422]:

def create_study_from_templates(ID, source_dir, output_dir="transmart_files", sec_req="Y", study_name=None):
    """


    :param ID:
    :param source_dir:
    :param output_dir:
    :param sec_req:
    :param study_name:
    :return:
    """
    study = TemplatedStudy(ID=ID, source_dir=source_dir, output_dir=output_dir, sec_req=sec_req)

    process_clinical(study)
    write_low_dim_params(study)
    process_high_dim(study)

    return epilogue()

#
# # In[424]:
#
# main(ID="DECODE_WP5_TEMPLATE", source_dir="templatos_finalos_nonfictivus_v2")
#
#


