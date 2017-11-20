from ..shared import TableRow
import pandas as pd


class ModifierDimension(TableRow):

    def __init__(self, study):
        super().__init__()

        self.df = pd.DataFrame(data={
            'modifier_path': study.Clinical.Modifiers.df.iloc[:, 0],
            'modifier_cd': study.Clinical.Modifiers.df.iloc[:, 1],
            'name_char': study.Clinical.Modifiers.df.iloc[:, 2]
        }, columns=self.columns)

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                None,  # modifier_path
                None,  # modifier_cd
                None,  # name_char
                None,  # modifier_blob
                None,  # update_date
                None,  # download_date
                None,  # import_date
                None,  # sourcesystem_cd
                None,  # upload_id
                None,  # modifier_level
                None,  # modifier_node_type
            ],
            index=[
                'modifier_path',
                'modifier_cd',
                'name_char',
                'modifier_blob',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'upload_id',
                'modifier_level',
                'modifier_node_type',
            ])
