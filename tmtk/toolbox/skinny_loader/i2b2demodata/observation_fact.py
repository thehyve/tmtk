from .. import Defaults

import pandas as pd
import arrow


class ObservationFact:

    def __init__(self, skinny, straight_to_disk=False):
        self.skinny = skinny

        rows = []
        # Loop through all variables in the clinical data and add a row
        for variable in self.skinny.study.Clinical.all_variables.values():
            if variable.data_label in Defaults.RESERVED_LIST:
                continue
            rows += [*self.build_row(variable)]

        self.df = pd.DataFrame(rows, columns=self.columns)

    def build_row(self, var):
        """
        Returns all observation fact rows for a given variable.

        :param var:
        :return:
        """
        subj_id = self.skinny.study.Clinical.get_subj_id_for_var(var)

        for i, value in enumerate(var.values):
            if not value:
                continue
            row = self.row

            row.encounter_num = -1
            row.patient_num = self.skinny.patient_mapping.map[subj_id.values[i]]
            row.concept_cd = var.concept_code
            row.provider_id = '@'
            row.start_date = arrow.now().isoformat(sep=' ')
            row.modifier_cd = var.modifier_code
            row.instance_num = 1
            row.trial_visit_num = self.skinny.trial_visit_dimension.map[var.trial_visit]
            row.valtype_cd = 'N' if var.is_numeric else 'T'
            row.tval_char = 'E' if var.is_numeric else value
            row.nval_num = value if var.is_numeric else None

            yield row

    @property
    def row(self):
        """
        :return: Row with defaults
        """
        return pd.Series(
            data=[
                None,  # encounter_num
                None,  # patient_num
                None,  # concept_cd
                None,  # provider_id
                None,  # start_date
                None,  # modifier_cd
                None,  # instance_num
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
