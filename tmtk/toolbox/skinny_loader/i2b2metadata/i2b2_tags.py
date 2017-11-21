from ..shared import TableRow, path_slash_all
from tmtk.utils import path_converter

import pandas as pd


class I2B2Tags(TableRow):

    def __init__(self, study):

        self.study = study
        super().__init__()

        self.df = pd.DataFrame({'path': study.Tags.df.iloc[:, 0],
                                'tag_type': study.Tags.df.iloc[:, 1],
                                'tag': study.Tags.df.iloc[:, 2],
                                'tags_idx': study.Tags.df.iloc[:, 3],
                                }, columns=self.columns)

        self.df.path = self.df.path.apply(lambda x:
                                          path_slash_all(path_converter('{}\\{}'.format(self.study.top_node, x)))
                                          )
        self.df.tags_idx = self.df.tags_idx.astype(pd.np.int64)

        self.df.iloc[:, 0] = self.df.index

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,  # tag_id
                None,  # path
                None,  # tag
                None,  # tag_type
                None,  # tags_idx
                None,  # tag_option_id
            ],
            index=[
                'tag_id',
                'path',
                'tag',
                'tag_type',
                'tags_idx',
                'tag_option_id'
            ])




