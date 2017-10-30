from ..i2b2metadata.i2b2_secure import I2B2Secure

import pandas as pd
import arrow
from tqdm import tqdm


class ObservationFact:

    def __init__(self, skinny, straight_to_disk=False):
        self.skinny = skinny
        self._now = arrow.now().isoformat(sep=' ')

        rows = []

        if not straight_to_disk:
            # Loop through all variables in the clinical data and add a row
            for variable in tqdm(self.skinny.study.Clinical.filtered_variables.values()):
                rows += [*self.build_rows(variable)]

            self.df = pd.DataFrame(rows, columns=self.columns)
        else:
            with open(straight_to_disk, 'w') as f:
                for variable in tqdm(self.skinny.study.Clinical.filtered_variables.values()):
                    for row in self.build_rows(variable):
                        f.write(row.to_csv(sep='\t'))

    def build_rows(self, var):
        """
        Returns all observation fact rows for a given variable.

        :param var:
        :return:
        """
        def set_value_fields(row_, value_, visual_attributes):
            """

            :param row_:
            :param value_:
            :param visual_attributes: visual attributes determine the type of variable (unfortunately).
            :return: updated row.
            """
            if visual_attributes == var.DATE:
                row_.valtype_cd = 'N'
                row_.tval_char = 'E'
                # Unix time
                row_.nval_num = arrow.get(value_).format('X')
                # UTC
                row_.observation_blob = value_

            elif visual_attributes == var.TEXT:
                row_.valtype_cd = 'B'
                row_.observation_blob = value_

            elif visual_attributes == var.NUMERIC:
                row_.valtype_cd = 'N'
                row_.tval_char = 'E'
                row_.nval_num = value_

            elif visual_attributes == var.CATEGORICAL:
                row_.valtype_cd = 'T'
                row_.tval_char = value_

            return row_

        # Preload these, so we don't have to get them for every value in the current variable
        modifiers = var.modifiers
        start_date = var.start_date
        subj_id = var.subj_id
        trial_visit = var.trial_visit
        visual_attributes = var.visual_attributes

        concept_cd = I2B2Secure.get_concept_identifier(var, self.skinny.study)

        for i, value in enumerate(var.values):

            if self.not_a_value(value):
                # Check if there are any modifier values for this 'normal' values
                # We want to insert an 'empty' normal observation if there are modified observations.
                # This is useful to annotated missing values.
                if all([self.not_a_value(mod.values[i]) for mod in modifiers]):
                    continue

            base_row = self.row
            base_row.patient_num = self.skinny.patient_mapping.map[subj_id.values[i]]
            base_row.concept_cd = concept_cd
            base_row.start_date = start_date.values[i] if start_date else None
            base_row.trial_visit_num = self.skinny.trial_visit_dimension.map[trial_visit]

            yield set_value_fields(base_row.copy(), value, visual_attributes)

            for modifier_variable in modifiers:

                modifier_value = modifier_variable.values[i]

                if self.not_a_value(modifier_value):
                    continue

                modifier_row = base_row.copy()
                modifier_row.modifier_cd = modifier_variable.modifier_code

                yield set_value_fields(modifier_row, modifier_value, modifier_variable.visual_attributes)

    @staticmethod
    def not_a_value(value) -> bool:
        return not value or pd.isnull(value)

    @property
    def row(self):
        """
        :return: Row with defaults
        """
        return pd.Series(
            data=[
                -1,    # encounter_num
                None,  # patient_num
                None,  # concept_cd
                '@',   # provider_id
                None,  # start_date
                '@',   # modifier_cd
                1,     # instance_num
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

    @property
    def columns(self):
        return self.row.keys()
