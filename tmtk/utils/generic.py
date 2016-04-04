import os
import webbrowser
import pandas as pd
import tmtk
from .exceptions import *


def file2df(path=None):
    """
    Load a file specified by path into a Pandas dataframe.

    :param path to file to load
    :returns pandas dataframe
    """
    if not os.path.exists(path):
        print(os.getcwd())
        print(path)
        print('file2df: File does not exist.')
    df = pd.read_table(path,
                       sep='\t',
                       dtype=object)
    return df


def df2file(df=None, path=None):
    """
    Write a dataframe to file properly
    :param df
    :param path
    """
    if not path:
        raise PathError
    df.to_csv(path=path,
              sep='\t',
              index=False,
              float_format='%.3f')
    pass


def call_boris(column_mapping=None, port=26747):
    """
    This function loads the Arborist if it has been properly installed in your environment.

    :param column_mapping has to be either a path to column mapping file or a tmtk.ColumnMapping object.
    :param port that the server should run on, defaults to 26747 (Boris).
    """
    import arborist
    if isinstance(column_mapping, tmtk.clinical.ColumnMapping):
        path = column_mapping.path
    elif os.path.exists(column_mapping):
        path = column_mapping
    else:
        print("No path to column mapping file or a valid ColumnMapping object given.")
    running_on = 'http://localhost:{}/treeview/{}'.format(port, path)
    print('Launching The Arborist now at {}.'.format(running_on))
    webbrowser.open(running_on, new=0, autoraise=True)
    arborist.app.run(port=port)


def validate_clinical_data(df):
    """
    This function takes a dataframe and checks whether transmart-batch can load this.

    :param df is a dataframe.
    :return True if passed, else tries to return error message.
    """
    pass


def find_column_datatype(df):
    """
    This function takes a dataframe and determines the whether transmart will interpret it as:
    categorical or numerical.

    :param df is a dataframe
    :return is a series of categorical and numerical.
    """
    pass


def get_unique_filename(first_filename):
    """
    Olafs functions.py
    """
    if not os.path.exists(first_filename):
        return first_filename

    postfix = None
    version = 1
    directory = os.path.dirname(first_filename)
    filename = os.path.basename(first_filename)
    parts = filename.split(".")
    if len(parts) > 1:
        postfix = "."+parts[-1]
        name = ".".join(parts[:-1])
    else:
        name = filename

    new_filename = "{}_{!s}{!s}".format(name, version, postfix)
    full_filename = os.path.join(directory, new_filename)

    while os.path.exists(full_filename):
        version += 1
        new_filename = "{}_{!s}{!s}".format(name, version, postfix)
        full_filename = os.path.join(directory, new_filename)
    else:
        return full_filename


def is_categorical(values):
    pass