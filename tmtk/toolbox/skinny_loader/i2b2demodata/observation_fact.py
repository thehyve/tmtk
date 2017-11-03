from ..shared import TableRow, get_concept_identifier

import pandas as pd
import arrow
from tqdm import tqdm


class ObservationFact(TableRow):
    def __init__(self, skinny, straight_to_disk=False):

        self.skinny = skinny
        self._now = arrow.now().isoformat(sep=' ')
        super().__init__()

        self.df = None

        if not straight_to_disk:
            self._build_in_memory()
        else:
            self.write_to_disk(straight_to_disk)

    def _build_in_memory(self):

        dfs = []
        # Loop through all variables in the clinical data and add a row
        for variable in tqdm(self.skinny.study.Clinical.filtered_variables.values()):
            dfs += [r for r in self.build_rows(variable)]

        self.df = pd.concat(dfs, ignore_index=True)

    def write_to_disk(self, path):
        with open(path, 'w') as f:
            f.write('\t'.join(self.columns) + '\n')
            for variable in tqdm(self.skinny.study.Clinical.filtered_variables.values()):
                pd.DataFrame(
                    [r for r in self.build_rows(variable)]
                ).to_csv(f, sep='\t', index=False, header=False)

    def build_rows(self, var):
        """
        Returns all observation fact rows for a given variable.
        """

        def get_value_fields(values, visual_attributes):
            """
            Update a row object with its value based on visual_attributes

            :param row_: row to modify
            :param value_: value to be set
            :param visual_attributes: visual attributes determine the type of variable (unfortunately).
            :return: updated row.
            """
            if visual_attributes == var.VIS_DATE:
                return {'valtype_cd': 'N',
                        'tval_char': 'E',
                        # Unix time
                        'nval_num': values.apply(lambda x: arrow.get(x).format('X')),
                        # UTC
                        'observation_blob': values}

            elif visual_attributes == var.VIS_TEXT:
                return {'valtype_cd': 'B',
                        'observation_blob': values}

            elif visual_attributes == var.VIS_NUMERIC:
                return {'valtype_cd': 'N',
                        'tval_char': 'E',
                        'nval_num': values}

            elif visual_attributes == var.VIS_CATEGORICAL:
                return {'valtype_cd': 'T',
                        'tval_char': values}

        # Preload these, so we don't have to get them for every value in the current variable
        modifiers = var.modifiers
        start_date = var.start_date
        subj_id = var.subj_id
        trial_visit = var.trial_visit
        visual_attributes = var.visual_attributes

        var_wide_data = {
            'encounter_num': -1,
            'patient_num': var.subj_id.values.apply(lambda x: self.skinny.patient_mapping.map[x]),
            'concept_cd': get_concept_identifier(var, self.skinny.study),
            'provider_id': '@',
            'start_date': start_date.values[i] if start_date else None,
            'modifier_cd': '@',
            'instance_num': 1}
        var_wide_data.update(get_value_fields(var.values, visual_attributes))

        df = pd.DataFrame(var_wide_data, columns=self.columns)
        yield df

    #         for i, (value, subj_id_value) in enumerate(zip(var.values, subj_id.values)):

    #             if self.not_a_value(value):
    #                 # Check if there are any modifier values for this 'normal' values
    #                 # We want to insert an 'empty' normal observation if there are modified observations.
    #                 # This is useful to annotated missing values.
    #                 if all([self.not_a_value(mod.values[i]) for mod in modifiers]):
    #                     continue

    #             base_row = self.row
    #             base_row.patient_num = self.skinny.patient_mapping.map[subj_id_value]

    #             base_row.concept_cd = concept_cd
    #             base_row.start_date = start_date.values[i] if start_date else None
    #             # trial visits other than 'General' are currently not supported
    #             base_row.trial_visit_num = self.skinny.trial_visit_dimension.map[trial_visit]

    #             yield set_value_fields(base_row.copy(), value, visual_attributes)

    #             for modifier_variable in modifiers:

    #                 modifier_value = modifier_variable.values[i]

    #                 if self.not_a_value(modifier_value):
    #                     continue

    #                 modifier_row = base_row.copy()
    #                 modifier_row.modifier_cd = modifier_variable.modifier_code

    #                 yield set_value_fields(modifier_row, modifier_value, modifier_variable.visual_attributes)

    @staticmethod
    def not_a_value(value) -> bool:
        return not value or pd.isnull(value)

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                -1,  # encounter_num
                None,  # patient_num
                None,  # concept_cd
                '@',  # provider_id
                None,  # start_date
                '@',  # modifier_cd
                1,  # instance_num
                None,  # trial_visit_num
                None,  # valtype_cd
                None,  # tval_char
                None,  # nval_num
                None,  # valueflag_cd
                None,  # quantity_num
                None,  # units_cd
                None,  # end_date
                None,  # location_cd
                None,  # observation_blob
                None,  # confidence_num
                None,  # update_date
                None,  # download_date
                None,  # import_date
                None,  # sourcesystem_cd
                None,  # upload_id
                None,  # sample_cd
            ],
            index=[
                'encounter_num',
                'patient_num',
                'concept_cd',
                'provider_id',
                'start_date',
                'modifier_cd',
                'instance_num',
                'trial_visit_num',
                'valtype_cd',
                'tval_char',
                'nval_num',
                'valueflag_cd',
                'quantity_num',
                'units_cd',
                'end_date',
                'location_cd',
                'observation_blob',
                'confidence_num',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'upload_id',
                'sample_cd',
            ])
