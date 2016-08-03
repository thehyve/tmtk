import pandas as pd
import os

from .DataFile import DataFile
from .Variable import VariableCollection
from .ColumnMapping import ColumnMapping
from .WordMapping import WordMapping
from ..utils import CPrint, PathError, clean_for_namespace
from .. import arborist


class Clinical:
    """
    Container class for all clinical information.
    """
    def __init__(self, clinical_params):
        self.ColumnMapping = ColumnMapping(params=clinical_params)
        self.WordMapping = WordMapping(params=clinical_params)
        self.Variables = VariableCollection(clinical_parent=self)
        self.params = clinical_params

        for file in self.ColumnMapping.included_datafiles:
            clinical_data_path = os.path.join(self.params.dirname, file)
            self.add_datafile(clinical_data_path)

    def add_datafile(self, filename, dataframe=None):
        """
        Add a clinical data file.
        :param filename: filename of file in clinical directory
        :param dataframe: if given, add pd.DataFrame to study.
        :return:
        """

        if isinstance(dataframe, pd.DataFrame):
            datafile = DataFile()
            datafile.df = dataframe

        else:
            if os.path.exists(filename):
                file_path = filename
            else:
                file_path = os.path.join(self.params.dirname, filename)
            assert os.path.exists(file_path), PathError(file_path)
            datafile = DataFile(file_path)

            # Check if file is in de clinical directory
            if not os.path.dirname(os.path.abspath(filename)) == self.params.dirname:
                datafile.df  # Force load df

        datafile.path = os.path.join(self.params.dirname, os.path.basename(filename))

        while self.get_datafile(datafile.name):
            new_name = input("Filename {!r} already taken, try again.  ".format(datafile.name))
            datafile.name = new_name or datafile.name  # Checking for empty string input

        safe_name = clean_for_namespace(datafile.name)
        self.__dict__[safe_name] = datafile

        if datafile.name not in self.ColumnMapping.included_datafiles:
            CPrint.okay('Adding {!r} as clinical datafile to study.'.format(datafile.name))
            self.ColumnMapping.append_from_datafile(datafile)

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

    def get_datafile(self, name):
        """
        Find datafile object by filename
        :param name: name of file
        :return: DataFile object
        """
        for key, obj in self.__dict__.items():
            if isinstance(obj, DataFile):
                if obj.name == name:
                    return obj
