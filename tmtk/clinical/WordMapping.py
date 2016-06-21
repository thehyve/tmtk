from tmtk import utils
import os
import pandas as pd
from tmtk.params import ClinicalParams


class WordMapping(utils.FileBase):
    """
    Base Class for word mapping file.
    """
    def __init__(self, params=None):

        self.params = params

        if not isinstance(params, ClinicalParams):
            raise utils.Exceptions.ClassError(type(params))
        elif params.__dict__.get('WORD_MAP_FILE'):
            self.path = os.path.join(params.dirname, params.WORD_MAP_FILE)
        else:
            self.path = os.path.join(params.dirname, 'word_mapping_file.txt')
            self.params.__dict__['WORD_MAP_FILE'] = os.path.basename(self.path)

        super().__init__()

    def validate(self, verbosity=2):
        pass

    def get_word_map(self, var_id):
        """

        Returns dict with value in data, and mapped value
        :param var_id:
        :return:
        """
        mapping_dict = {}

        filename, column = var_id.rsplit('__', 1)
        f = self.df.ix[:, 0].astype(str) == filename
        c = self.df.ix[:, 1].astype(str) == column
        if sum(f & c):
            # fill dict with col3 as key and col4 as value
            # self.df.ix[f & c].apply(lambda x: mapping_dict.update({x[2]: x[3]}), axis=1)
            self.df.ix[f & c].apply(lambda x: mapping_dict.update({x[2]: x[3].replace('+', '&')}), axis=1)
        return mapping_dict

    @staticmethod
    def create_df():
        df = pd.DataFrame(dtype=str, columns=['Filename',
                                              'Column Number',
                                              'Datafile Value',
                                              'Mapping Value'])
        return df
