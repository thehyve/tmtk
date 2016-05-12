from .DataFile import DataFile
from .Variable import VariableCollection
from .ColumnMapping import ColumnMapping
from .WordMapping import WordMapping
from tmtk import arborist, utils
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

        col_map_row = self.ColumnMapping.get_data_args(var_id)

        concept_path = '{}\\{}'.format(col_map_row[1], col_map_row[3])

        data_args = {FILENAME: col_map_row[0],
                     CATEGORY_CODE: col_map_row[1],
                     COLUMN_NUMBER: col_map_row[2],
                     DATA_LABEL: col_map_row[3],
                     MAGIC_5: col_map_row[4] if len(col_map_row) > 4 else None,
                     MAGIC_6: col_map_row[5] if len(col_map_row) > 5 else None,
                     }

        return variable, concept_path, data_args

    def call_boris(self):
        self.ColumnMapping.df = arborist.call_boris(self)

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)