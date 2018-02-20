import os
import shutil
import time
from IPython.display import display, IFrame, clear_output
import tempfile
import json

from ..utils import Message, ClassError, ArboristException

from .jstreecontrol import create_concept_tree, ConceptTree
import tmtk


def call_boris(study=None, **kwargs):
    """
    This function loads the Arborist if it has been properly installed in your environment.

    :param study: a <tmtk.Study> object.
    """

    if not isinstance(study, tmtk.Study):
        Message.error("Have to provide a tmtk.Study object.")
        raise ClassError(type(study, 'tmtk.Study'))

    concept_tree = create_concept_tree(study)

    try:
        ontology_tree = study.Clinical.OntologyMapping.as_json()
    except AttributeError:
        ontology_tree = None

    if ontology_tree:
        ver2_data = {"version": "2",
                     "concept_tree": concept_tree,
                     "ontology_tree": ontology_tree}

        json_data = json.dumps(ver2_data)

    else:
        json_data = concept_tree

    json_data = launch_arborist_gui(json_data, **kwargs)  # Returns modified json_data

    if json_data:
        Message.okay('Successfully closed The Arborist. The updated column'
                     ' mapping file has been returned as a dataframe.')
        Message.warning("Don't forget to save this dataframe to disk if you want to store it.")
    else:
        raise ArboristException('No json file returned from Arborist.')

    update_study_from_json(study, json_data=json_data)


def launch_arborist_gui(json_data: str, height=650):
    """
    :param json_data: json data to launch the Arborist with.
    :param height: IFrame height for output cell.
    """

    new_temp_dir = tempfile.mkdtemp()
    tmp_json = os.path.join(new_temp_dir, 'tmp_json')

    with open(tmp_json, 'w') as f:
        f.write(json_data)

    # Signal created by Javascript to continue work here.
    done_signal = os.path.join(os.path.dirname(tmp_json), 'DONE')

    base_url = os.environ.get("ARBORIST_BASE_URL", "/")

    running_on = '{}transmart-arborist?treefile={}'.format(base_url, os.path.abspath(tmp_json))
    display(IFrame(src=running_on, width='100%', height=height))

    try:
        # Wait for the done signal file to be created before breaking the GIL.
        while not os.path.exists(done_signal):
            time.sleep(0.1)

    except KeyboardInterrupt:
        # This stops the interpreter without showing a stacktrace.
        pass

    else:
        updated_json = None

        # We've been having issues with a slow file system where the json response was empty
        # Now we make sure something is sent back.
        while not updated_json:
            time.sleep(0.1)
            with open(tmp_json, 'r') as f:
                updated_json = f.read()

        return updated_json

    finally:
        shutil.rmtree(new_temp_dir)
        # Clear output from Jupyter Notebook cell
        clear_output()
        print('Cleaning up before closing...')


def update_study_from_json(study, json_data):
    """
    Update an existing tmtk.Study object with the JSON response from the Arborist.

    :param study: tmtk.Study object.
    :param json_data: json response from Arborist.
    """

    concept_tree = ConceptTree(json_data)
    study.Clinical.ColumnMapping.df = concept_tree.column_mapping_file
    study.Clinical.WordMapping.df = concept_tree.word_mapping

    # Some checks for whether to create Tags in the study.
    ct_tags = concept_tree.tags_file
    if hasattr(study, 'Tags') or ct_tags.shape[0]:
        study.ensure_metadata()
        study.Tags.df = concept_tree.tags_file

    high_dim_paths = concept_tree.high_dim_paths
    if high_dim_paths:
        study.HighDim.update_high_dim_paths(high_dim_paths)
