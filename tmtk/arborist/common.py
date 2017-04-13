import os
import pandas as pd
import shutil
import time
from IPython.display import display, IFrame, clear_output
import tempfile

from ..utils import CPrint
from .. import utils

from .jstreecontrol import create_concept_tree, ConceptTree
import tmtk


def call_boris(to_be_shuffled=None, **kwargs):
    """
    This function loads the Arborist if it has been properly installed in your environment.

    :param to_be_shuffled: has to be either a tmtk.Study object, a Pandas
        column mapping dataframe, or a path to column mapping file.
    """

    if isinstance(to_be_shuffled, str) and os.path.exists(to_be_shuffled):
        to_be_shuffled = utils.file2df(to_be_shuffled)
        return_df = True

    if isinstance(to_be_shuffled, (pd.DataFrame, tmtk.Clinical, tmtk.Study)):
        pass

    else:
        CPrint.error("No path to column mapping file or a valid object given.")
        raise utils.ClassError(type(to_be_shuffled, 'pd.DataFrame, tmtk.Clinical or tmtk.Study'))

    json_data = create_concept_tree(to_be_shuffled)

    json_data = launch_arborist_gui(json_data, **kwargs)  # Returns modified json_data

    if isinstance(to_be_shuffled, tmtk.Study):
        update_study_from_json(to_be_shuffled, json_data=json_data)
    elif isinstance(to_be_shuffled, tmtk.Clinical):
        update_clinical_from_json(to_be_shuffled, json_data=json_data)
    else:
        return ConceptTree(json_data).column_mapping_file


def launch_arborist_gui(json_data: str, height=650):
    """

    :param json_data:
    :param height:
    :return:
    """

    new_temp_dir = tempfile.mkdtemp()
    tmp_json = os.path.join(new_temp_dir, 'tmp_json')

    with open(tmp_json, 'w') as f:
        f.write(json_data)

    original_time = int(os.path.getmtime(tmp_json))

    base_url = os.environ.get("ARBORIST_BASE_URL", "/")

    running_on = '{}transmart-arborist?treefile={}'.format(base_url, os.path.abspath(tmp_json))
    display(IFrame(src=running_on, width='100%', height=height))

    # Wait for the json file to change before breaking the GIL.
    while original_time == int(os.path.getmtime(tmp_json)):
        time.sleep(0.25)

    # Clear output from Jupyter Notebook cell
    clear_output()

    CPrint.okay('Successfully closed The Arborist. The updated column mapping file '
                'has been returned as a dataframe.')
    CPrint.warn("Don't forget to save this dataframe to disk if you want to store it.")

    with open(tmp_json, 'r') as f:
        json_data = f.read()

    shutil.rmtree(new_temp_dir)

    return json_data


def update_clinical_from_json(clinical, json_data):
    """

    :param clinical:
    :param json_data:
    :return:
    """
    concept_tree = ConceptTree(json_data)
    clinical.ColumnMapping.df = concept_tree.column_mapping_file
    clinical.WordMapping.df = concept_tree.word_mapping


def update_study_from_json(study, json_data):
    """

    :param study:
    :param json_data:
    :return:
    """

    concept_tree = ConceptTree(json_data)
    study.Clinical.ColumnMapping.df = concept_tree.column_mapping_file
    study.Clinical.WordMapping.df = concept_tree.word_mapping

    # Some checks for whether to create Tags in the study.
    ct_tags = concept_tree.tags_file
    if hasattr(study, 'Tags') or ct_tags.shape[0]:
        study.add_metadata()
        study.Tags.df = concept_tree.tags_file

    high_dim_paths = concept_tree.high_dim_paths
    if high_dim_paths:
        study.HighDim.update_high_dim_paths(high_dim_paths)
