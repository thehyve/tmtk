from .. import Defaults

from ..i2b2metadata.i2b2_secure import I2B2Secure

import pandas as pd
import arrow


class ObservationFact:

    VALUETYPE_CD_MAP = {
        'LAD': 'N',
        'LAT': 'B',
        'LAN': 'N',
        'LAC': 'T'
    }

    def __init__(self, skinny, straight_to_disk=False):
        self.skinny = skinny
        self._now = arrow.now().isoformat(sep=' ')

        rows = []
        # Loop through all variables in the clinical data and add a row
        for variable in self.skinny.study.Clinical.filtered_variables.values():
            rows += [*self.build_rows(variable)]

        self.df = pd.DataFrame(rows, columns=self.columns)

    def build_rows(self, var):
        """
        Returns all observation fact rows for a given variable.

        :param var:
        :return:
        """
        subj_id = self.skinny.study.Clinical.get_subj_id_for_var(var)
        concept_cd = I2B2Secure.get_concept_identifier(var, self.skinny.study)

        valtype_cd = self.VALUETYPE_CD_MAP.get(var.visual_attributes)

        for i, value in enumerate(var.values):
            if not value:
                continue
            row = self.row

            row.patient_num = self.skinny.patient_mapping.map[subj_id.values[i]]
            row.concept_cd = concept_cd
            row.start_date = self._now
            row.trial_visit_num = self.skinny.trial_visit_dimension.map[var.trial_visit]
            row.valtype_cd = valtype_cd
            row.tval_char = 'E' if var.is_numeric else value
            row.nval_num = value if valtype_cd == 'N' else None

            yield row

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
