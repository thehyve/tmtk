import csv
import os
from glob import glob

from tmtk.toolbox import template_validation as Validity


class TemplatedStudy:
    def __init__(self, ID, source_dir, output_dir="transmart_files", sec_req="Y", name=None):
        self.ID = ID
        self.name = name
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.sec_req = sec_req

        self.clinical_template_present = True
        self.metadata_output_dir = os.path.join(self.output_dir, "tags")
        self.clin_output_dir = os.path.join(self.output_dir, "clinical")
        self.col_map_rows = set()
        self.word_map_rows = set()
        self.all_metadata = set()
        self.hd_dict = {}
        self.hd_dir_level_metadata = {}
        self.col_map_file_name = self.ID + "_column_mapping.tsv"
        self.word_map_file_name = self.ID + "_word_mapping.tsv"
        self.metadata_file_name = self.ID + "_tags.tsv"
        self.tree_sheet_name = None
        self.word_map_sheet_name = None
        self.col_map_header = ("Filename", "Category Code", "Column Number", "Data Label", "Data Label Source",
                               "Control Vocab Cd", "Concept Type")
        self.word_map_header = ("Filename", "Column Number", "Datafile Value", "Mapping Value")
        self.metadata_header = ("concept_key", "tag_title", "tag_description", "index")

        Validity.check_source_dir(source_dir)
        Validity.check_output_dir(output_dir)
        self.excel_files = [excel_file for excel_file in glob(self.source_dir + "/*.xls*")]
        os.makedirs(self.clin_output_dir, exist_ok=True)

    def _sort_write(self, data, key1, key2, output_path, header):
        """Sort and write the input data."""
        data_as_list = list(data)
        data_as_list.sort(key=lambda x: (x[key1], x[key2]))

        with open(output_path, "w") as output_file:
            writer = csv.writer(output_file, delimiter='\t', quotechar=None)
            writer.writerow(header)
            writer.writerows(data_as_list)

    def write_column_mapping(self):
        """Sort rows on data file and column number, then write the column mapping rows."""
        output_path = os.path.join(self.clin_output_dir, self.col_map_file_name)
        self._sort_write(self.col_map_rows, 0, 2, output_path, self.col_map_header)
        print("Column mapping file written at: {0}".format(output_path))

    def write_word_mapping(self):
        """Sort rows on data file and column nubmer, then write the word mapping rows."""
        if self.word_map_rows:
            output_path = os.path.join(self.clin_output_dir, self.word_map_file_name)
            self._sort_write(self.word_map_rows, 0, 1, output_path, self.word_map_header)
            print("Word mapping file written at: {0}".format(output_path))

    def write_metadata(self):
        """Sort rows on concept_path and tag index, then write the metadata rows."""
        if self.all_metadata:
            os.makedirs(self.metadata_output_dir, exist_ok=True)
            output_path = os.path.join(self.metadata_output_dir, self.metadata_file_name)
            self._sort_write(self.all_metadata, 0, 3, output_path, self.metadata_header)

    def _add_dir_level_metadata(self, path, platform_id, platform_name):
        if path not in self.hd_dir_level_metadata:
            self.hd_dir_level_metadata[path] = HdDirLevelMetadata(platform_id, platform_name)
        else:
            self.hd_dir_level_metadata[path]._expand_existing(platform_id, platform_name)

    def _finalize_dir_level_metadata(self):
        """Add the collected dir level metadata to the all_metadata set."""
        for path, metadata in self.hd_dir_level_metadata.items():
            platform_ids = ", ".join(metadata.platform_ids)
            platform_names = ", ".join(metadata.platform_names)
            self.all_metadata.add((path, "Platform names", platform_names, 10))
            self.all_metadata.add((path, "Platform IDs", platform_ids, 11))


class HdDirLevelMetadata:
    def __init__(self, platform_id, platform_name):
        self.platform_ids = {platform_id}
        self.platform_names = {platform_name}

    def _expand_existing(self, platform_id, platform_name):
        self.platform_ids.add(platform_id)
        self.platform_names.add(platform_name)


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
