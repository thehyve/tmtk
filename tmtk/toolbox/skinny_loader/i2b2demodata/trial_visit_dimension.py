from ..shared import TableRow, Defaults

import pandas as pd


class TrialVisitDimension(TableRow):

    def __init__(self, study):
        super().__init__()
        self.df = pd.DataFrame([self.build_row(trial_visit) for trial_visit in study.Clinical.get_trial_visits()],
                               columns=self.columns)

        self.df.iloc[:, 0] = self.df.index
        self.df.study_num = self.df.study_num.astype(pd.np.int64)

        self.map = dict(zip(self.df.rel_time_label, self.df.trial_visit_num))

    def build_row(self, trial_visit):
        row = self.row

        row.rel_time_label = trial_visit.get('name')
        row.rel_time_num = trial_visit.get('relative_time')
        row.rel_time_unit_cd = trial_visit.get('time_unit')

        return row

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,                 # trial_visit_num
                Defaults.STUDY_NUM,   # study_num
                None,                 # rel_time_unit_cd
                None,                 # rel_time_num
                None,                 # rel_time_label
            ],
            index=[
                'trial_visit_num',
                'study_num',
                'rel_time_unit_cd',
                'rel_time_num',
                'rel_time_label',
            ])
