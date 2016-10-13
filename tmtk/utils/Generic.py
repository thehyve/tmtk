import os
import pandas as pd
import random
from IPython.display import YouTubeVideo
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


def file2df(path=None):
    """
    Load a file specified by path into a Pandas dataframe.  If hashed is True, return a
    a (dataframe, hash) value tuple.

    :param path: to file to load
    :return: `pd.DataFrame`
    """
    if not os.path.exists(path):
        raise PathError('File ({}) does not exist.'.format(path))
    df = pd.read_table(path,
                       sep='\t',
                       dtype=object)
    return df


def md5(s: str):
    """
    utf-8 encoded md5 hash string of input s.

    :param s: string
    :return: md5 hash string
    """
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def df2file(df=None, path=None, overwrite=False):
    """
    Write a dataframe to file safely.  Does not overwrite existing files
    automatically. This function converts concept path delimiters.

    :param df: `pd.DataFrame`
    :param path: path to write to
    :param overwrite: False (default) or True
    """
    if not path:
        raise PathError(path)

    if not overwrite and os.path.exists(path):
        raise PathError("{} already exists. Consider setting `overwrite=True`".format(path))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.replace(Mappings.PATH_DELIM, '\\\\', inplace=True, regex=True)

    df.to_csv(path,
              sep='\t',
              index=False,
              float_format='%.3f')


def find_fully_unique_columns(df):
    """
    Check if a dataframe contains a fully unique column (SUBJ_ID candidate).

    :param df: `pd.DataFrame`
    :return: list of names of unique columns
    """

    unique_cols = df.apply(lambda x: len(x.unique()) == len(df))
    return list(df.columns[unique_cols])


def is_numeric(values):
    """
    Check if list of values are numeric.

    :param values: iterable
    """
    for v in values:
        if not numeric(v):
            return False
    return True


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
    return YouTubeVideo('dQw4w9WgXcQ', autoplay=True)


def path_converter(path, delimiter=None):
    """
    Convert paths by creating delimiters of backslash "\" and "+" sign, additionally converting
    underscores "_" to a single space.

    :param path: concept path
    :param delimiter: delimiter for paths, defaults to Mappings.path_delim
    :return: delimited path
    """

    if not delimiter:
        delimiter = Mappings.PATH_DELIM

    path = re.sub(r'[\\+]', delimiter, path)
    return path.strip(delimiter)


def path_join(*args):
    """
    Join items with the used path delimiter.

    :param args: path items
    :return: path as string
    """
    return Mappings.PATH_DELIM.join(args)


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def column_map_diff(a_column, b_column):

    column_map = {}

    for k in set().union(a_column, b_column):
        if not a_column.get(k):
            column_map[k] = ('-', b_column[k])
        elif not b_column.get(k):
            column_map[k] = (a_column[k], '-')
        elif a_column[k] != b_column[k]:
            column_map[k] = (a_column[k], b_column[k])

    return column_map


def word_map_diff(a_word_map, b_word_map):

    word_map = {}

    for k in set().union(a_word_map, b_word_map):

        if not a_word_map.get(k):
            word_map[k] = b_word_map[k]
        elif not b_word_map.get(k):
            word_map[k] = a_word_map[k]
        else:
            d = {}
            for dfv in set().union(a_word_map[k], b_word_map[k]):
                a_mapped = a_word_map[k].get(dfv)
                b_mapped = b_word_map[k].get(dfv)

                if not a_mapped and a_mapped != "":
                    d[dfv] = b_mapped

                elif not b_mapped and b_mapped != "":
                    d[a_mapped] = dfv

                elif a_mapped != b_mapped:
                    d[a_mapped] = b_mapped

            if d:
                word_map[k] = d

    return word_map
