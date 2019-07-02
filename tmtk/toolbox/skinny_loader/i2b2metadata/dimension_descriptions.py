from ..shared import TableRow

import pandas as pd


class DimensionDescription(TableRow):

    def __init__(self, study):

        self.study = study
        super().__init__()

        self.df = pd.DataFrame([self.build_row_from_study_dimension(d) for d in study.get_dimensions()],
                               columns=self.columns)

        # Add additional information for the modifiers
        self.adapt_rows_from_modifier_dimension()

        self.df.iloc[:, 0] = self.df.index

    def build_row_from_study_dimension(self, dimension: str):
        row = self.row
        # Cannot use dot notation here because name is an attribute of
        # pd.Series and that causes a collision.
        row['name'] = dimension

        # Hardcoded patient dimension properties
        if dimension == 'patient':
            row['dimension_type'] = 'SUBJECT'
            row['sort_index'] = '1'

        return row

    def adapt_rows_from_modifier_dimension(self):

        def adapt_df_row(x):

            modifier_row = self.df.name == x[2]
            if not any(modifier_row):
                return

            size = len(x)
            self.df.loc[modifier_row, 'modifier_code'] = x[1]
            self.df.loc[modifier_row, 'value_type'] = 'T' if x[3] == 'CATEGORICAL' else 'N'
            if size > 4:
                self.df.loc[modifier_row, 'dimension_type'] = x[4]
            if size > 5:
                self.df.loc[modifier_row, 'sort_index'] = x[5]

            # Some hardcoded stuff
            self.df.loc[modifier_row, 'density'] = 'DENSE'
            self.df.loc[modifier_row, 'packable'] = 'NOT_PACKABLE'
            self.df.loc[modifier_row, 'size_cd'] = 'SMALL'

        if self.study.Clinical.Modifiers:
            self.study.Clinical.Modifiers.df.apply(adapt_df_row, axis=1)

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,  # id
                None,  # density
                None,  # modifier_code
                None,  # value_type
                None,  # name
                None,  # packable
                None,  # size_cd
                None,  # dimension_type
                None,  # sort_index
            ],
            index=[
                'id',
                'density',
                'modifier_code',
                'value_type',
                'name',
                'packable',
                'size_cd',
                'dimension_type',
                'sort_index'
            ])
