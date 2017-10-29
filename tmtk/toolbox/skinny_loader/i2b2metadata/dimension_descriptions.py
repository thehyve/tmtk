import pandas as pd
import os


class DimensionDescription:

    def __init__(self, study):
        self.df = pd.DataFrame(
            {'name': study.get_dimensions()},
            columns=self.columns
        )

        self.df.iloc[:, 0] = self.df.index


    @property
    def columns(self):
        return ['id',
                'density',
                'modifier_code',
                'value_type',
                'name',
                'packable',
                'size_cd',
                ]
