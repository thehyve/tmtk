from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join

import os
import json


# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="transmart-arborist",
        # _also_ in the `nbextension/` namespace
        require="transmart-arborist/placeholder",
    )]


def _jupyter_server_extension_paths():
    return [{
        "module": "tmtk.arborist"
    }]


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'

    base_url = web_app.settings['base_url']

    # Put url prefix (e.g. '/user/madonna/') in environment as hack to open iframe later
    os.environ["ARBORIST_BASE_URL"] = base_url

    nb_server_app.log.info("Started loading transmart-arborist extension.")

    route_pattern = url_path_join(base_url, 'transmart-arborist')

    web_app.add_handlers(host_pattern, [(route_pattern, TransmartArborist)])

    template_dir = os.path.join(os.path.dirname(__file__), "static")

    def _try_for_searchpath(obj):
        try:
            obj.searchpath.append(template_dir)
            return True
        except AttributeError:
            pass

    # Add template path to jinja2 searchpath for notebook
    searchpath_found = _try_for_searchpath(web_app.settings["jinja2_env"].loader)

    if not searchpath_found:
        # Add template path to jinja2 searchpath for the hub
        for obj in web_app.settings["jinja2_env"].loader.loaders:
            searchpath_found = _try_for_searchpath(obj)

    if not searchpath_found:
        nb_server_app.log.error("Arborist Warning: jinja2 template search path not found.")
    else:
        nb_server_app.log.info("The transmart-arborist module enabled!")


class TransmartArborist(IPythonHandler):
    """
    Implement the handler for transmart-arborist on the jupyter server.
    """

    def get(self):

        # Get location of json in tmp
        tmp_json = self.request.arguments.get('treefile')[0]

        self.log.info("Launching Arborist.")

        with open(tmp_json, 'r') as f:
            treejson = json.loads(f.read())

        try:
            if treejson.get('version') == "2":
                ontology_tree = treejson.get('ontology_tree')
                concept_tree = treejson.get('concept_tree')
        except AttributeError:
            concept_tree = json.dumps(treejson)
            ontology_tree = {}

        static_base = '{}nbextensions/transmart-arborist/'.format(self.base_url)

        self.finish(self.render_template("jupyter_embedded.html",
                                         concept_tree=concept_tree,
                                         ontology_tree=ontology_tree,
                                         base_url=self.base_url,
                                         static_base=static_base))

    def post(self):

        # Get location of json in tmp
        tmp_file = self.request.headers.get("Referer").rsplit('treefile=', 1)[1]

        # A file that is created after the json is fully written to disk.
        # This serves as a signal for the parent kernel to continue work.
        done_file = os.path.join(os.path.dirname(tmp_file), 'DONE')

        self.log.info("Saving Arborist tree file.")

        with open(tmp_file, 'w') as f:
            f.write(json.dumps(self.get_json_body()))

        with open(done_file, 'w') as f:
            f.write('')

        self.finish("200")
