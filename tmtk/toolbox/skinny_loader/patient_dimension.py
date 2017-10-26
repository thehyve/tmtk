import pandas as pd


class PatientDimension:

    def __init__(self, study):
        self.study = study

        self.df = pd.DataFrame(
            [self.build_row(id_, age_gender) for id_, age_gender in study.Clinical.get_patients().items()],
            columns=self.columns)

        self.df.iloc[:, 0] = self.df.index

    @staticmethod
    def build_row(patient_id, age_gender):

        return pd.Series({
            'sex_cd': age_gender.get('gender'),
            'age_in_years_num': age_gender.get('age'),
            'sourcesystem_cd': patient_id,
        })

    @property
    def columns(self):
        return ['patient_num',
                'vital_status_cd',
                'birth_date',
                'death_date',
                'sex_cd',
                'age_in_years_num',
                'language_cd',
                'race_cd',
                'marital_status_cd',
                'religion_cd',
                'zip_cd',
                'statecityzip_path',
                'income_cd',
                'patient_blob',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'upload_id',
                ]
