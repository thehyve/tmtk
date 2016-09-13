import pandas as pd
import os

from .DataFile import DataFile
from .Variable import Variable, VarID
from .ColumnMapping import ColumnMapping
from .WordMapping import WordMapping
from ..utils import CPrint, PathError, clean_for_namespace
from .. import arborist


class Clinical:
    """
    Container class for all clinical data related objects, i.e. the column
    mapping, word mapping, and clinical data files.

    This object has methods that add data files, and for lookups of clinical
    files and variables.
    """

    def __init__(self, clinical_params):
        self.ColumnMapping = ColumnMapping(params=clinical_params)
        self.WordMapping = WordMapping(params=clinical_params)
        self.params = clinical_params

        for file in self.ColumnMapping.included_datafiles:
            clinical_data_path = os.path.join(self.params.dirname, file)
            self.add_datafile(clinical_data_path)

    def add_datafile(self, filename, dataframe=None):
        """
        Add a clinical data file to study.

        :param filename: path to file or filename of file in clinical directory.
        :param dataframe: if given, add `pd.DataFrame` to study.
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
            datafile.name = new_name if not new_name == '' else datafile.name

        safe_name = clean_for_namespace(datafile.name)
        self.__dict__[safe_name] = datafile

        if datafile.name not in self.ColumnMapping.included_datafiles:
            CPrint.okay('Adding {!r} as clinical datafile to study.'.format(datafile.name))
            self.ColumnMapping.append_from_datafile(datafile)

    def get_variable(self, var_id: tuple):
        """
        Return a Variable object based on variable id.

        :param var_id: tuple of filename and column number.
        :return: `tmtk.Variable`.
        """
        df_name, column = var_id
        datafile = self.get_datafile(df_name)
        return Variable(datafile, column, self)

    @property
    def all_variables(self):
        """
        Dictionary where {`tmtk.VarID`: `tmtk.Variable`} for all variables in
        the column mapping file.
        """
        return {VarID(var_id): self.get_variable(var_id) for var_id in self.ColumnMapping.ids}

    def call_boris(self):
        """
        Use The Arborist to modify only information in the column and word mapping files.
        """
        arborist.call_boris(self)

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)

    def get_datafile(self, name: str):
        """
        Find datafile object by filename.

        :param name: name of file.
        :return: `tmtk.DataFile` object.
        """
        for key, obj in self.__dict__.items():
            if isinstance(obj, DataFile):
                if obj.name == name:
                    return obj

    def __hash__(self):
        """
        Calculate hash for in memory pd.DataFrame objects.  The sum of these hashes
        is returned.

        :return: sum of hashes.
        """
        hashes = 0
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'df'):
                hashes += hash(obj)
        return hashes

    def show_changes(self):
        """Print changes made to the column mapping and word mapping file."""
        column_changes = self.ColumnMapping.path_changes(silent=True)
        word_map_changes = self.WordMapping.word_map_changes(silent=True)

        for var_id in set().union(column_changes, word_map_changes):
            print("{}: {}".format(*var_id))
            path_change = column_changes.get(var_id)
            if path_change:
                print("       {}".format(path_change[0]))
                print("    -> {}".format(path_change[1]))
            else:
                print("       {}".format(self.get_variable(var_id).concept_path))

            map_change = word_map_changes.get(var_id)
            if map_change:
                for k, v in map_change.items():
                    print("          - {!r} -> {!r}".format(k, v))
