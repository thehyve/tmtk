import os
import pandas as pd

from ..utils import FileBase, Exceptions, Mappings
from ..params import ClinicalParams


class Modifiers(FileBase):
    """
    Class representing the modifiers file.
    """

    def __init__(self, params=None):
        """
        Initialize by giving a params object.

        :param params: `tmtk.ClinicalParams`.
        """

        self.params = params

        if not isinstance(params, ClinicalParams):
            raise Exceptions.ClassError(type(params))
        elif params.get('MODIFIERS_FILE'):
            self.path = os.path.join(params.dirname, params.MODIFIERS_FILE)
        else:
            self.path = os.path.join(params.dirname, 'modifiers_file.txt')
            self.params.__dict__['MODIFIERS_FILE'] = os.path.basename(self.path)

        super().__init__()

    def build_index(self, df=None):
        """
        Build index for the column mapping dataframe.  If `pd.DataFrame`
        (optional) is given, modify and return that.

        :param df: `pd.DataFrame`.
        :return: `pd.DataFrame`.
        """
        if not isinstance(df, pd.DataFrame):
            df = self.df
        df.set_index(df.columns[1], drop=False, inplace=True)
        df.sort_index(inplace=True)
        return df

    def create_df(self):
        """
        Create `pd.DataFrame` with a correct header and base reference values for modifiers.

        :return: `pd.DataFrame`.
        """
        df = pd.DataFrame(dtype=str,
                          columns=Mappings.modifiers_header,
                          data={
                              'modifier_path': ['\Missing Value', '\Sample_id'],
                              'modifier_cd': ['MISSVAL', 'SAMPLE_ID'],
                              'name_char': ['Missing Value','Sample identifier'],
                              'Data Type': ['CATEGORICAL', 'CATEGORICAL'],
                              'dimension_type': ['ATTRIBUTE', 'SUBJECT'],
                              'sort_index': [3, 2]}
                          )
        df = self.build_index(df)
        return df
