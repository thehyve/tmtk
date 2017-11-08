from ..shared import TableRow, Defaults

import pandas as pd
import json


class StudyTable(TableRow):

    def __init__(self, study):
        super().__init__()

        self.df = pd.DataFrame(
            data={
                'study_num': Defaults.STUDY_NUM,
                'study_id': study.study_id,
                'secure_obj_token': study.study_id if study.security_required else Defaults.PUBLIC_TOKEN,
                'study_blob': json.dumps(study.study_blob)},
            columns=self.columns,
            index=[0])

        self.df.iloc[:, 0] = self.df.index
        self.df.iloc[:, 0].astype(pd.np.int64, inplace=True)

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,  # study_num
                None,  # bio_experiment_id
                None,  # study_id
                None,  # secure_obj_token
                None,  # study_blob
            ],
            index=[
                'study_num',
                'bio_experiment_id',
                'study_id',
                'secure_obj_token',
                'study_blob',
            ])
