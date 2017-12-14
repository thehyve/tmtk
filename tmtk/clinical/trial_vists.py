import os
import pandas as pd

from ..utils import FileBase, Exceptions, Mappings
from ..params import ClinicalParams


class TrialVisits(FileBase):
    """
    Class representing the trial visits file.
    """

    def __init__(self, params=None):
        """
        Initialize by giving a params object.

        :param params: `tmtk.ClinicalParams`.
        """

        self.params = params

        if not isinstance(params, ClinicalParams):
            raise Exceptions.ClassError(type(params))
        elif params.get('TRIAL_VISITS_FILE'):
            self.path = os.path.join(params.dirname, params.TRIAL_VISITS_FILE)
        else:
            self.path = os.path.join(params.dirname, 'trial_visits.tsv')
            self.params.__dict__['TRIAL_VISITS_FILE'] = os.path.basename(self.path)

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
        df.set_index(df.columns[0], drop=False, inplace=True)
        df.sort_index(inplace=True)
        return df

    def create_df(self):
        """
        Create `pd.DataFrame` with a correct header.

        :return: `pd.DataFrame`.
        """
        df = pd.DataFrame(dtype=str, columns=Mappings.trial_visits_header)
        df = self.build_index(df)
        return df
