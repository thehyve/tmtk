import pandas as pd
from .patient_dimension import PatientDimension


class PatientMapping:

    def __init__(self, patient_dimension: PatientDimension):
        self.df = pd.DataFrame({'patient_ide': patient_dimension.df.sourcesystem_cd,
                                'patient_ide_source': 'SUBJ_ID',
                                'patient_num': patient_dimension.df.patient_num},
                               columns=self.columns)

        # A dictionary that can be queried for internal identifier mapping.
        self.map = dict(zip(self.df.patient_ide, self.df.patient_num))

    @property
    def columns(self):
        return ['patient_ide',
                'patient_ide_source',
                'patient_num',
                'patient_ide_status',
                'upload_date',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'upload_id',
                ]
