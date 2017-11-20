from ..shared import TableRow
import pandas as pd


class PatientDimension(TableRow):

    def __init__(self, study):
        self.study = study
        super().__init__()

        # Due to implementation details on pd.from_dict() method we need to add
        # something to the patients dictionary if neither age or gender are present.
        patient_dict = self.study.Clinical.get_patients()
        patient_dict.update({p: {'age': pd.np.nan} for p, v in patient_dict.items() if not v})

        self.df = pd.DataFrame.from_dict(patient_dict, orient='index')
        self.df.reset_index(drop=False, inplace=True)

        # Due to non deterministic behaviour of dictionaries need to check the order
        # in the temporary dataframe.
        new_columns = list(self.df.columns)
        new_columns[0] = 'sourcesystem_cd'

        try:
            new_columns[new_columns.index('age')] = 'age_in_years_num'

            # Database will round, so we have to floor age here.
            self.df.age = self.df.age.astype(pd.np.float64) // 1
        except ValueError:
            pass

        try:
            new_columns[new_columns.index('gender')] = 'sex_cd'
        except ValueError:
            pass

        self.df.columns = new_columns

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
