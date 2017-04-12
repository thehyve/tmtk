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
        # require="transmart-arborist/nbextension",
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
    route_pattern = url_path_join(web_app.settings['base_url'], 'transmart-arborist')
    web_app.add_handlers(host_pattern, [(route_pattern, TransmartArborist)])
    nb_server_app.log.info("The transmart-arborist module enabled!")

    web_app.settings["jinja2_env"].loader.searchpath += [
        os.path.join(os.path.dirname(__file__), "static")
    ]


class TransmartArborist(IPythonHandler):
    """
    Implement the handler for transmart-arborist on the jupyter server.
    """

    def get(self):

        # Get location of json in tmp
        tmp_json = self.request.arguments.get('treefile')[0]

        with open(tmp_json, 'r') as f:
            treejson = f.read()

        self.finish(self.render_template("jupyter_embedded.html",
                                         json=treejson,
                                         treeview=True,
                                         **self.application.settings))

    def post(self):

        # Get location of json in tmp
        tmp_file = self.request.headers.get("Referer").rsplit('treefile=', 1)[1]

        with open(tmp_file, 'w') as f:
            f.write(json.dumps(self.get_json_body()))
        self.finish("200")
