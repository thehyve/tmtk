from ..shared import TableRow, Defaults, calc_hlevel, get_full_path, path_slash_all, path_converter

import pandas as pd
import uuid
from tqdm import tqdm


class I2B2Secure(TableRow):

    def __init__(self, study, concept_dimension):

        self.study = study
        self.concept_dimension = concept_dimension
        super().__init__()

        # To be used for faster lookups in add_missing_paths method
        self._paths_set = set()

        row_list = [self.build_variable_row(var) for var in tqdm(study.Clinical.filtered_variables.values())]
        row_list += [r for r in self.add_top_nodes()]

        self.df = pd.DataFrame(row_list, columns=self.columns)

        # Add Ontology paths as nodes in tree. This creates paths in i2b2_secure for
        # each term defined in ontology mapping.
        self.back_populate_ontology(concept_dimension)

        # Add 'unmapped' variables from i2b2_secure to concept dimension
        self.concept_dimension.add_one_timer_concepts(self)

        # We have to go back to add all missing folders
        self.add_missing_folders()

    @staticmethod
    def sanitize_path(path):
        """ Convert paths and ensure start and end with single backslash """
        return path_slash_all(path_converter(path))

    def build_variable_row(self, var):
        """ Create a row for a variable object. """

        row = self.row
        row.c_fullname = get_full_path(var, self.study)
        row.c_hlevel = calc_hlevel(row.c_fullname)
        row.c_name = var.data_label
        row.c_visualattributes = var.visual_attributes
        row.c_basecode = var.concept_code or str(uuid.uuid4())
        row.c_dimcode = self.concept_dimension.get_path_for_code(var.concept_code) or row.c_fullname

        return row

    def add_top_nodes(self):
        """
        Generate add study node itself and any preceding nodes as 'CA' containers.
        """

        row = self.row

        row.c_fullname = self.sanitize_path(self.study.top_node)
        row.c_hlevel = calc_hlevel(row.c_fullname)
        row.c_visualattributes = 'FAS'
        row.c_facttablecolumn = '@'
        row.c_tablename = 'STUDY'
        row.c_columnname = 'STUDY_ID'
        row.c_operator = '='
        row.c_name = path_converter(self.study.study_name)
        row.c_dimcode = self.study.study_id

        yield row

        parent_nodes = row.c_fullname.strip(Defaults.DELIMITER).split(Defaults.DELIMITER)
        path = Defaults.DELIMITER
        for i, parent in enumerate(parent_nodes[:-1]):
            row = row.copy()
            path = '{}{}{}'.format(path, parent, Defaults.DELIMITER)
            row.c_fullname = path
            row.c_name = parent
            row.c_hlevel = i
            row.c_visualattributes = 'CA'
            row.c_tablename = '@'
            row.c_columnname = '@'
            row.c_dimcode = '@'
            row.secure_obj_token = Defaults.PUBLIC_TOKEN
            row.sourcesystem_cd = None

            yield row

    def back_populate_ontology(self, concept_dimension):
        """ Create rows for ontology terms. """
        for concept_row in concept_dimension.df.itertuples():
            concept_code = concept_row[1]
            concept_path = concept_row[2]
            concept_name = concept_row[3]
            row = self.df[self.df.c_basecode == concept_code].copy()
            row.c_fullname = concept_path
            row.c_hlevel = calc_hlevel(concept_path)
            row.c_name = concept_name
            row.sourcesystem_cd = None
            row.secure_obj_token = Defaults.PUBLIC_TOKEN
            self.df = self.df.append(row, ignore_index=True, verify_integrity=False)

    def add_missing_folders(self):
        """ Add rows for all parent folders not present yet. """
        self._paths_set = set(self.df.c_fullname)
        self.df.apply(lambda x: self._add_folders(x.c_fullname), axis=1)

    def _add_folders(self, path):
        """ Strips the path leaf and adds it to the frame if it does not exist. """
        parent = path.rsplit('\\', 2)[0] + '\\'
        if parent == '\\':
            return
        if parent not in self._paths_set:
            self.add_folder_row(parent)
        self._add_folders(parent)

    def add_folder_row(self, path):
        row = self.row
        row.c_fullname = path
        row.c_dimcode = path
        row.c_hlevel = calc_hlevel(path)
        row.c_name = path.strip(Defaults.DELIMITER).split(Defaults.DELIMITER)[-1]

        if not path.startswith(self.sanitize_path(self.study.top_node)):
            row.sourcesystem_cd = None
            row.secure_obj_token = Defaults.PUBLIC_TOKEN

        self._paths_set.add(path)
        self.df = self.df.append(row, ignore_index=True, verify_integrity=False)

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,                   # c_hlevel
                None,                   # c_fullname
                None,                   # c_name
                'N',                    # c_synonym_cd
                'FA',                   # c_visualattributes
                None,                   # c_totalnum
                None,                   # c_basecode
                None,                   # c_metadataxml
                'CONCEPT_CD',           # c_facttablecolumn
                'CONCEPT_DIMENSION',    # c_tablename
                'CONCEPT_PATH',         # c_columnname
                'T',                    # c_columndatatype
                'LIKE',                 # c_operator
                None,                   # c_dimcode
                None,                   # c_comment
                None,                   # c_tooltip
                '@',                    # m_applied_path
                None,                   # update_date
                None,                   # download_date
                None,                   # import_date
                self.study.study_id,    # sourcesystem_cd
                None,                   # valuetype_cd
                None,                   # m_exclusion_cd
                None,                   # c_path
                None,                   # c_symbol
                None,                   # i2b2_id
                self.study.study_id if self.study.security_required else Defaults.PUBLIC_TOKEN],   # secure_obj_token
            index=[
                'c_hlevel',
                'c_fullname',
                'c_name',
                'c_synonym_cd',
                'c_visualattributes',
                'c_totalnum',
                'c_basecode',
                'c_metadataxml',
                'c_facttablecolumn',
                'c_tablename',
                'c_columnname',
                'c_columndatatype',
                'c_operator',
                'c_dimcode',
                'c_comment',
                'c_tooltip',
                'm_applied_path',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'valuetype_cd',
                'm_exclusion_cd',
                'c_path',
                'c_symbol',
                'i2b2_id',
                'secure_obj_token'])
