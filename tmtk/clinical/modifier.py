import os
import pandas as pd
import json

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

    def create_df(self):
        """
        Create `pd.DataFrame` with a correct header.

        :return: `pd.DataFrame`.
        """
        df = pd.DataFrame(dtype=str, columns=Mappings.modifiers_header)
        # df = self.build_index(df)
        return df
