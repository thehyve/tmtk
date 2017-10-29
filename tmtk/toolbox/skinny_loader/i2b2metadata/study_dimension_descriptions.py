from .. import Defaults

import pandas as pd


class StudyDimensionDescription:

    def __init__(self, dimension_description):

        row_list = []
        for dimension_id in dimension_description.df['id']:
            row = self.row
            row.dimension_description_id = dimension_id
            row_list.append(row)

        self.df = pd.DataFrame(row_list)


    @property
    def row(self):
        """
        :return: Row with defaults
        """
        return pd.Series(
            data=[
                None,                # dimension_description_id
                Defaults.STUDY_NUM,  # study_id
            ],
            index=[
                'dimension_description_id',
                'study_id',
            ])

    @property
    def columns(self):
        return self.row.keys()
