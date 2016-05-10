from .DataFile import DataFile
from .Variable import VariableCollection
from .ColumnMapping import *
from .WordMapping import *
import tmtk.utils as utils
import pandas as pd
import os

FILENAME = 'Filename'
CATEGORY_CODE = 'Category Code'
COLUMN_NUMBER = 'Column Number'
DATA_LABEL = 'Data Label'
MAGIC_5 = 'Data Label Source'
MAGIC_6 = 'Control Vocab Cd'


class Clinical:
    """
    Container class for all clinical information.
    """
    def __init__(self, clinical_params):
        self.ColumnMapping = ColumnMapping(params=clinical_params)
        self.WordMapping = WordMapping(params=clinical_params)
        self.Variables = VariableCollection()
        self.clinical_dirname = clinical_params.dirname

        for file in self.ColumnMapping.included_datafiles:
            clinical_data_path = os.path.join(file)
            self.add_datafile(clinical_data_path)

    def add_datafile(self, filename, dataframe=None):
        """
        Add a clinical data file.
        :param filename: filename of file in clinical directory
        :param dataframe: if given, add pd.DataFrame to study.
        :return:
        """
        if isinstance(filename, str):
            file_path = os.path.join(self.clinical_dirname, filename)
        else:
            raise utils.PathError(filename)

        if not dataframe:
            assert os.path.exists(file_path), utils.PathError(file_path)
            clinical_data_file = DataFile(file_path)

        elif isinstance(dataframe, pd.DataFrame):
            raise utils.NotYetImplemented

        safe_name = utils.clean_for_namespace(filename)
        self.__dict__[safe_name] = clinical_data_file
        self.Variables.add_datafile(clinical_data_file)

    def get_variable(self, var_id: str):
        """
        Give var_id (<filename>__<column>, e.g. 'Cell-line-data__3' and get concept path
        and variable object.
        :param var_id: string <filename>__<column>
        :return: tuple of tmtk.clinical.Variable, concept_path
        """
        variable = self.Variables.get(var_id)
        concept_path = self.ColumnMapping.get_concept_path(var_id)

        filename, column = var_id.rsplit('__', 1)

        data_args = {FILENAME: filename,
                     CATEGORY_CODE: self.ColumnMapping.get_category_cd(var_id),
                     COLUMN_NUMBER: column,
                     DATA_LABEL: self.ColumnMapping.get_data_label(var_id),
                     MAGIC_5: self.ColumnMapping.get_magic5(var_id),
                     MAGIC_6: self.ColumnMapping.get_magic6(var_id),
                     }

        return variable, concept_path, data_args

    def call_boris(self):
        self.ColumnMapping.df = utils.call_boris(self)
