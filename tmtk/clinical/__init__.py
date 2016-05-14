from .DataFile import DataFile
from .Variable import VariableCollection
from .ColumnMapping import ColumnMapping
from .WordMapping import WordMapping
from tmtk import arborist, utils
import pandas as pd
import os


class Clinical:
    """
    Container class for all clinical information.
    """
    def __init__(self, clinical_params):
        self.ColumnMapping = ColumnMapping(params=clinical_params)
        self.WordMapping = WordMapping(params=clinical_params)
        self.Variables = VariableCollection(clinical_parent=self)
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
        :return: a tmtk.clinical.Variable
        """
        variable = self.Variables.get(var_id)

        return variable

    def call_boris(self):
        arborist.call_boris(self)

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)
