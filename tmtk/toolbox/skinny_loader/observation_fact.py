import pandas as pd
import arrow


class ObservationFact:

    def __init__(self, skinny):
        self.skinny = skinny

        rows = []
        # Loop through all variables in the clinical data and add a row
        for variable in self.skinny.study.Clinical.all_variables.values():
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

            yield pd.Series({
                'encounter_num': -1,
                'patient_num': self.skinny.patient_mapping.map[subj_id.values[i]],
                'concept_cd': var.concept_code,
                'provider_id': '@',
                'start_date': arrow.now().isoformat(sep=' '),
                'modifier_cd': var.modifier_code,
                'instance_num': 1,
                'trial_visit_num': self.skinny.trial_visit_dimension.map[var.trial_visit],
                'valtype_cd': 'N' if var.is_numeric else 'T',
                'tval_char': 'E' if var.is_numeric else value,
                'nval_num': value if var.is_numeric else None,
                'valueflag_cd': None,
                'quantity_num': None,
                'units_cd': None,
                'end_date': None,
                'location_cd': None,
                'observation_blob': None,
                'confidence_num': None,
                # 'update_date': None,
                # 'download_date': None,
                # 'import_date': None,
                'sourcesystem_cd': None,
                'upload_id': None,
                'sample_cd': None,
            })


    @property
    def columns(self):
        return ['encounter_num',
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
                ]
