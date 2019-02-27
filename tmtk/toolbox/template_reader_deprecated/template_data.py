import csv
import operator
import os
from glob import glob

import pandas as pd

from . import template_validation as Validity


class TemplatedStudy:
    def __init__(self, ID, source_dir, output_dir=None, sec_req="Y"):
        self.ID = str(ID).upper()
        self.name = None
        self.source_dir = source_dir
        if not output_dir:
            output_dir = self.ID + "_transmart_files"
        self.output_dir = output_dir
        self.sec_req = sec_req.upper()

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
        self.excel_files = [excel_file for excel_file in glob(self.source_dir + "/*.xls*") if "~$" not in excel_file]
        os.makedirs(self.clin_output_dir, exist_ok=True)

    def _sort_write(self, data, output_path, header, *args):
        """Sort and write the input data."""
        data_as_list = list(data)
        data_as_list.sort(key=operator.itemgetter(*args))

        with open(output_path, "w") as output_file:
            writer = csv.writer(output_file, delimiter='\t', quotechar=None)
            writer.writerow(header)
            writer.writerows(data_as_list)

    def write_column_mapping(self):
        """Sort rows on data file and column number, then write the column mapping rows."""
        output_path = os.path.join(self.clin_output_dir, self.col_map_file_name)
        self._sort_write(self.col_map_rows, output_path, self.col_map_header, 0, 2)
        print("[INFO] Column mapping file written at: {0}".format(output_path))

    def write_word_mapping(self):
        """Sort rows on data file and column nubmer, then write the word mapping rows."""
        if self.word_map_rows:
            output_path = os.path.join(self.clin_output_dir, self.word_map_file_name)
            self._sort_write(self.word_map_rows, output_path, self.word_map_header, 0, 1, 2)
            print("[INFO] Word mapping file written at: {0}".format(output_path))

    def write_metadata(self):
        """Sort rows on concept_path and tag index, then write the metadata rows."""
        if self.all_metadata:
            os.makedirs(self.metadata_output_dir, exist_ok=True)
            output_path = os.path.join(self.metadata_output_dir, self.metadata_file_name)
            self._sort_write(self.all_metadata, output_path, self.metadata_header, 0, 3)

    def add_dir_level_metadata(self, path, platform_id, platform_name):
        if path not in self.hd_dir_level_metadata:
            self.hd_dir_level_metadata[path] = HdDirLevelMetadata(platform_id, platform_name)
        else:
            self.hd_dir_level_metadata[path]._expand_existing(platform_id, platform_name)

    def finalize_dir_level_metadata(self):
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

    class Sheets:
        def __init__(self):
            self.metadata_samples = None
            self.platform = None
            self.data = None

    def __init__(self):
        self.workbook_name = None
        self.output_dir = None
        self.hd_type = None
        self.organism = None
        self.platform_id = None
        self.platform_name = None
        self.genome_build = None
        self.annotation_params_name = None
        self.hd_data_params_name = None
        self.sheets = HighDim.Sheets()

    def read_hd_file_template(self, source_dir, hd_template):
        """Try to read the specified template file and send to sheet loading method."""
        template_path = os.path.join(source_dir, hd_template)
        try:
            hd_template_workbook = pd.ExcelFile(template_path)
        except FileNotFoundError:
            raise Validity.TemplateException("Could not find high-dim template file at: {0}".format(template_path))
        # except XLRDError:
        #     raise Validity.TemplateException(
        #         "High-dim template file at: {0} is not a valid xlsx file.".format(template_path))

        self._load_sheets(hd_template_workbook)

    def _load_sheets(self, hd_template):
        """Check which sheets are present in the high-dim template and store them."""
        hd_sheets = hd_template.sheet_names

        attributes = {"metadata_samples":
                          {"keyword": "metadata&samples", "comment": None, "converters": None},
                      "data":
                          {"keyword": "matrix", "comment": "#", "converters": None},
                      "platform":
                          {"keyword": "platform", "comment": "#", "converters":
                              {"CHROMOSOME": str, "START_BP": str, "END_BP": str, "NUM_PROBES": str}}
                      }

        for attribute, params in attributes.items():
            hits = [sheet for sheet in hd_sheets if params["keyword"] in sheet.lower()]
            if len(hits) > 1 or (attribute == "metadata_samples" and len(hits) == 0):
                Validity.list_length(hits, expected=1)
            elif len(hits) == 0:
                print("[WARNING] No {0} sheet found in {1}".format(attribute, self.workbook_name))
            else:
                hd_df = hd_template.parse(hits[0], comment=params["comment"], converters=params["converters"])
                empty = Validity.empty_df(hd_df, mandatory=False, df_name=attribute, workbook_name=self.workbook_name)
                if not empty:
                    setattr(self.sheets, attribute, hd_df)
