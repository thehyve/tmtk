from .. import Defaults

import pandas as pd


class StudyDimensionDescription:

    def __init__(self, dimension_description):
        self.df = pd.DataFrame(
            {'dimension_description_id': dimension_description.df['id'],
             'study_id': Defaults.STUDY_NUM},
            columns=self.columns)

    @property
    def columns(self):
        return ['dimension_description_id',
                'study_id',
                ]
