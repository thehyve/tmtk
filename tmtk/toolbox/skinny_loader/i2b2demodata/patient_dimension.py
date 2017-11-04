from ..shared import TableRow
import pandas as pd


class PatientDimension(TableRow):

    def __init__(self, study):
        self.study = study
        super().__init__()

        self.df = pd.DataFrame.from_dict(study.Clinical.get_patients(), orient='index')
        self.df.reset_index(drop=False, inplace=True)
        self.df.columns = ['sourcesystem_cd', 'age_in_years_num', 'sex_cd']
        self.df = self.df.reindex(columns=self.columns)

        self.df.iloc[:, 0] = self.df.index

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,  # patient_num
                None,  # vital_status_cd
                None,  # birth_date
                None,  # death_date
                None,  # sex_cd
                None,  # age_in_years_num
                None,  # language_cd
                None,  # race_cd
                None,  # marital_status_cd
                None,  # religion_cd
                None,  # zip_cd
                None,  # statecityzip_path
                None,  # income_cd
                None,  # patient_blob
                None,  # update_date
                None,  # download_date
                None,  # import_date
                None,  # sourcesystem_cd
                None,  # upload_id
            ],
            index=[
                'patient_num',
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
            ])
