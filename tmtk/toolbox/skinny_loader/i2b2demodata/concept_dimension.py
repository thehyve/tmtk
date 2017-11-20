from ..shared import TableRow, path_slash_all

import pandas as pd


class ConceptDimension(TableRow):

    def __init__(self, study, i2b2_secure):
        self.study = study
        super().__init__()

        row_list = []
        if study.Clinical.OntologyMapping and study.Clinical.OntologyMapping.df.shape[0] > 1:
            row_list += [self._build_ontology_row(c)
                         for c in study.Clinical.OntologyMapping.tree.get_concept_rows()]

        self.df = pd.DataFrame(row_list, columns=self.columns)

        # Add Ontology paths as nodes in tree. This creates paths in i2b2_secure for
        # each term defined in ontology mapping.
        i2b2_secure.back_populate_ontology(self)

        # Add 'unmapped' variables from i2b2_secure to concept dimension
        self._add_one_timer_concepts(i2b2_secure)

        # Put back the right order of columns after concatenating the two dataframes
        self.df = self.df.reindex(columns=self.columns)

        self.map = dict(zip(self.df.concept_path, self.df.concept_cd))

    def _add_one_timer_concepts(self, i2b2_secure):
        """
        All variables are represented in i2b2_secure, though some might not have
        been mapped to an ontology code via the column mapping file. This method adds
        'project specific' concepts to the concept dimension.
        """
        # Find all concept nodes in i2b2 secure by checking for visualattributes starting with LA
        variable_nodes = i2b2_secure.df.c_visualattributes.str.startswith('LA')
        current_concept_codes = set(self.df.concept_cd)
        unmapped_concepts = i2b2_secure.df.c_basecode.apply(lambda x: x not in current_concept_codes)

        # Bool vector operation to find i2b2_secure rows that are variables and not mapped.
        to_be_mapped = variable_nodes & unmapped_concepts
        # Subset and transform to concept_dimension rows.
        tmp_df = i2b2_secure.df.loc[to_be_mapped, ['c_basecode', 'c_fullname', 'c_name']]
        tmp_df.columns = self.columns[:3]

        self.df = self.df.append(tmp_df, ignore_index=True)

    def _build_ontology_row(self, concept):
        row = self.row
        row.concept_cd, cpath, row.name_char, row.concept_blob = concept
        # Ensure slashes in first and last position for robustness
        row.concept_path = path_slash_all(cpath)
        return row

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,  # concept_cd
                None,  # concept_path
                None,  # name_char
                None,  # concept_blob
                None,  # update_date
                None,  # download_date
                None,  # import_date
                None,  # sourcesystem_cd
                None,  # upload_id
                None,  # table_name
            ],
            index=[
                'concept_cd',
                'concept_path',
                'name_char',
                'concept_blob',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'upload_id',
                'table_name'
            ])
