from ..shared import TableRow, Defaults

import pandas as pd


class StudyDimensionDescription(TableRow):

    def __init__(self, dimension_description):
        super().__init__()
        row_list = []
        for dimension_id in dimension_description.df['id']:
            row = self.row
            row.dimension_description_id = dimension_id
            row_list.append(row)

        self.df = pd.DataFrame(row_list)
        self.df.dimension_description_id = self.df.dimension_description_id.astype(pd.np.int64)
        self.df.study_id = self.df.study_id.astype(pd.np.int64)

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,                # dimension_description_id
                Defaults.STUDY_NUM,  # study_id
            ],
            index=[
                'dimension_description_id',
                'study_id',
            ])
