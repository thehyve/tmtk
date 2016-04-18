import os
import webbrowser
import pandas as pd
import tmtk
import random
import shutil
from .Exceptions import *
from IPython.display import display, Audio, IFrame, clear_output
import tempfile
from tmtk.utils.CPrint import CPrint


def clean_for_namespace(path) -> str:
    """
    Converts a path and returns a namespace safe variant. Converts characters that give errors
    to underscore.
    :param path: usually a descriptive subdirectory
    :return: string
    """
    disallowed = ['/', '-', ' ', '.']
    for item in disallowed:
        path = path.replace(item, '_')
    return path


def summarise(list_or_dict=None, max_items: int = 7) -> str:
    """
    Takes an iterable and returns a summarized string statement. Picks a random sample
    if number of items > max_items.

    :param list_or_dict: list or dict to summarise
    :param max_items: maximum number of items to keep.
    :return: the items joined as string with end statement.
    """
    unique_list = set(list(list_or_dict))
    n_uniques = len(unique_list)
    if n_uniques == 1:
        return str(unique_list.pop())
    if n_uniques > max_items:
        unique_list = random.sample(unique_list, max_items)
        end_statement = "({}) more".format(n_uniques - max_items)
    else:
        end_statement = "{}".format(unique_list.pop())

    first_statement = ", ".join(map(str, unique_list))

    m = "{} and {}".format(first_statement, end_statement)
    return m


def file2df(path=None):
    """
    Load a file specified by path into a Pandas dataframe.

    :param path to file to load
    :returns pandas dataframe
    """
    if not os.path.exists(path):
        raise PathError('file2df: File does not exist.')
    df = pd.read_table(path,
                       sep='\t',
                       dtype=object)
    return df


def df2file(df=None, path=None, overwrite=False):
    """
    Write a dataframe to file properly
    :param df:
    :param path:
    :param overwrite: False (default) or True.

    """
    if not path:
        raise PathError(path)

    if not overwrite and os.path.exists(path):
        raise PathError("{} already exists.")

    df.to_csv(path,
              sep='\t',
              index=False,
              float_format='%.3f')


def call_boris(column_mapping=None, port=26747):
    """
    This function loads the Arborist if it has been properly installed in your environment.

    :param column_mapping: has to be either a path to column mapping file or a tmtk.ColumnMapping object.
    :param port: that the server should run on, defaults to 26747 (Boris).
    """
    import arborist
    new_temp_dir = tempfile.mkdtemp()

    if isinstance(column_mapping, tmtk.clinical.ColumnMapping):
        path = column_mapping.path
        tmp_path = os.path.join(new_temp_dir, 'tmp_col_map.tsv')
        df2file(column_mapping.df, tmp_path)
    elif os.path.exists(column_mapping):
        path = column_mapping
        tmp_path = shutil.copy(path, new_temp_dir)
    else:
        CPrint.error("No path to column mapping file or a valid ColumnMapping object given.")

    running_on = 'http://localhost:{}/treeview/{}'.format(port, os.path.abspath(tmp_path))
    display(IFrame(src=running_on, width=900, height=900))
    arborist.app.run(port=port)
    clear_output()
    CPrint.okay('Successfully closed The Arborist. The updated column mapping file '
                'has been returned as a dataframe.')
    CPrint.warn("Don't forget to save this dataframe to disk if you want to store it.")
    return file2df(tmp_path)


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
    raise NotYetImplemented


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
    raise NotYetImplemented


def fix_everything():
    return Audio(os.path.join(os.path.dirname(__file__), 'fix_for_all_tm_loading_issues.mp3'),
                 autoplay=True)
