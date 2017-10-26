import pandas as pd

DEFAULT_TRIAL_VISIT = 'General'


class TrialVisitDimension:

    def __init__(self, study):

        self.df = pd.DataFrame([self.build_row(trial_visit) for trial_visit in study.Clinical.get_trial_visits()],
                               columns=self.columns)

        self.df.iloc[:, 0] = self.df.index
        self.map = dict(zip(self.df.rel_time_label, self.df.trial_visit_num))

    @staticmethod
    def build_row(trial_visit):
        return pd.Series({
            'rel_time_label': trial_visit.get('name'),
            'study_num': 0,
            'rel_time_num': trial_visit.get('relative_time'),
            'rel_time_unit_cd': trial_visit.get('time_unit'),
        })

    @property
    def columns(self):
        return ['trial_visit_num',
                'study_num',
                'rel_time_unit_cd',
                'rel_time_num',
                'rel_time_label',
                ]
