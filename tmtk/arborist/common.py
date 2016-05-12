import socket
import os
import pandas as pd
import random
import shutil
from IPython.display import display, Audio, IFrame, clear_output
import tempfile
from tmtk.utils.CPrint import CPrint
import tmtk
from .jstreecontrol import create_concept_tree, ConceptTree

feedback_categories = ['errors', 'warnings', 'infos']


def get_feedback_dict():
    feedback_dict = {}
    for feedback_category in feedback_categories:
        feedback_dict[feedback_category] = []
    return feedback_dict


def merge_feedback_dicts(*args):
    feedback_dict = get_feedback_dict()
    for arg in args:
        for feedback_category in feedback_categories:
            if feedback_category in arg:
                feedback_dict[feedback_category] += arg[feedback_category]
            else:
                msg = "Feedback category {} missing.".format(feedback_category)
                raise Exception(msg)
    return feedback_dict


def call_boris(to_be_shuffled=None):
    """
    This function loads the Arborist if it has been properly installed in your environment.

    :param to_be_shuffled: has to be either a tmtk.Study object, a Pandas
    column mapping dataframe, or a path to column mapping file.
    """

    if isinstance(to_be_shuffled, str) and os.path.exists(to_be_shuffled):
        to_be_shuffled = file2df(to_be_shuffled)
        return_df = True

    if isinstance(to_be_shuffled, (pd.DataFrame, tmtk.Clinical, tmtk.Study)):
        pass

    else:
        CPrint.error("No path to column mapping file or a valid ColumnMapping object given.")

    json_data = create_concept_tree(to_be_shuffled)

    json_data = launch_arborist_gui(json_data)  # Returns modified json_data

    if isinstance(to_be_shuffled, tmtk.Study):
        pass
    else:
        return ConceptTree(json_data).column_mapping_file


def launch_arborist_gui(json_data: str):

    from .flask_connection import app

    new_temp_dir = tempfile.mkdtemp()
    tmp_json = new_temp_dir + '/tmp_json'

    with open(tmp_json, 'w') as f:
        f.write(json_data)

    port = get_open_port()
    running_on = 'http://localhost:{}/treeview/{}'.format(port, os.path.abspath(tmp_json))
    display(IFrame(src=running_on, width=900, height=900))

    app.run(port=port)
    clear_output()

    CPrint.okay('Successfully closed The Arborist. The updated column mapping file '
                'has been returned as a dataframe.')
    CPrint.warn("Don't forget to save this dataframe to disk if you want to store it.")

    with open(tmp_json, 'r') as f:
        json_data = f.read()

    shutil.rmtree(new_temp_dir)

    return json_data


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
