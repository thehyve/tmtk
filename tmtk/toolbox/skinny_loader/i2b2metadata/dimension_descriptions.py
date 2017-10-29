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
    def row(self):
        """
        :return: Row with defaults
        """
        return pd.Series(
            data=[
                None,  #id
                None,  #density
                None,  #modifier_code
                None,  #value_type
                None,  #name
                None,  #packable
                None,  #size_cd
            ],
            index=[
                'id',
                'density',
                'modifier_code',
                'value_type',
                'name',
                'packable',
                'size_cd',
            ])

    @property
    def columns(self):
        return self.row.keys()
