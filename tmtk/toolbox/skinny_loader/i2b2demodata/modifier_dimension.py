import pandas as pd


class ModifierDimension:

    def __init__(self, study):
        assert all([c in self.columns for c in study.Clinical.Modifiers.df.columns]), \
            'Not all columns are legal.'

        self.df = pd.DataFrame(columns=self.columns).append(study.Clinical.Modifiers.df)

    @property
    def columns(self):
        return ['modifier_path',
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
                ]
