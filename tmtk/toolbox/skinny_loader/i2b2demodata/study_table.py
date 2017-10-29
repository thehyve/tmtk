from .. import Defaults

import pandas as pd


class StudyTable:

    def __init__(self, study):
        self.df = pd.DataFrame(
            data={
                'study_num': Defaults.STUDY_NUM,
                'study_id': study.study_id,
                'secure_obj_token': study.study_id if study.security_required else Defaults.PUBLIC_TOKEN,
                'study_blob': study.study_blob},
            columns=self.columns,
            index=[0])

        self.df.iloc[:, 0] = self.df.index

    @property
    def columns(self):
        return ['study_num',
                'bio_experiment_id',
                'study_id',
                'secure_obj_token',
                'study_blob',
                ]
