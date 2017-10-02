import pandas as pd


class ConceptDimension:

    def __init__(self, study):
        self.study = study

        row_list = [self._build_ontology_row(c) for c in study.Clinical.OntologyMapping.tree.get_concept_rows()]

        self.df = pd.DataFrame(row_list, columns=self.columns)

    def _build_ontology_row(self, concept):
        concept_cd, concept_path, name_char = concept

        return pd.Series({
            'concept_cd': concept_cd,
            'concept_path': concept_path,
            'name_char': name_char,
            'concept_blob': {}
        })

    @property
    def columns(self):
        return ['concept_cd',
                'concept_path',
                'name_char',
                'concept_blob',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'upload_id',
                'table_name',
                ]
