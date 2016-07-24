import os
import pandas as pd
import random
from IPython.display import Audio
import hashlib
import re

from .Exceptions import *
from .mappings import Mappings


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


def file2df(path=None, hashed=False):
    """
    Load a file specified by path into a Pandas dataframe.  If hashed is True, return a
    a (dataframe, hash) value tuple.

    :param path to file to load
    :param hashed:
    :returns pandas dataframe
    """
    if not os.path.exists(path):
        raise PathError('File ({}) does not exist.'.format(path))
    df = pd.read_table(path,
                       sep='\t',
                       dtype=object)
    if hashed:
        hash_value = hash(df.__bytes__())
        return df, hash_value
    else:
        return df


def md5(s: str):
    """
    utf-8 encoded md5 hash string of input s
    :param s: string
    :return: md5 hash string
    """
    return hashlib.md5(s.encode('utf-8')).hexdigest()


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
        raise PathError("{} already exists. Consider setting `overwrite=True`".format(path))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path,
              sep='\t',
              index=False,
              float_format='%.3f')


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


def is_numeric(values, hard=True):
    """
    Olafs functions.py
    """
    bool_list = [numeric(value) for value in values]

    if hard:
        return all(bool_list)
    else:
        return sum(bool_list) / len(bool_list)


def numeric(x):
    try:
        if x != 'inf':
            float(x)
            return True
    except ValueError:
        return False


def fix_everything():
    """
    Scans over all the data and indicates which errors have been fixed. This
    function is great for stress relieve.
    :return: All your problems fixed by Rick
    """
    return Audio(os.path.join(os.path.dirname(__file__), 'fix_for_all_tm_loading_issues.mp3'),
                 autoplay=True)


def path_converter(path, delimiter=None):
    """
    Convert paths by creating delimiters of backslash "\" and "+" sign, additionally converting
    underscores "_" to a single space.
    :param path: concept path
    :param delimiter: delimiter for paths, defaults to Mappings.path_delim
    :return: delimited path
    """

    if not delimiter:
        delimiter = Mappings.path_delim

    path = re.sub(r'[\\+]', delimiter, path)
    return path.strip(delimiter)


def path_join(*args):
    """
    :param args:
    :return:
    """
    return Mappings.path_delim.join(args)
