#!/usr/bin/env python3
import os
import sys

from flask import Flask, request, render_template, json
from werkzeug.routing import BaseConverter

import urllib
from markupsafe import Markup

app = Flask(__name__)

app.secret_key = 'not_so_secret'

app.jinja_env.add_extension("jinja2.ext.do")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.filters['path_join'] = lambda paths: os.path.join(*paths)


def add_slash_if_not_windows(url_path):
    if sys.platform != 'win32':
        url_path = '/' + url_path
    return url_path


def single_forward_slashed(string):
    """
    Converts string so that all double and backslashes for a single forward slash.

    :param string: input string
    :return: returns the new string
    """
    string = string.replace('//', '/')
    string = string.replace('\\', '/')
    return string


class FolderPathConverter(BaseConverter):
    def __init__(self, url_map):
        super(FolderPathConverter, self).__init__(url_map)
        self.regex = '.*'

    def to_python(self, value):
        value = add_slash_if_not_windows(value)
        value = single_forward_slashed(value)
        return value

    def to_url(self, value):
        value = single_forward_slashed(value)
        return value


app.url_map.converters['folderpath'] = FolderPathConverter


@app.template_filter('urlencode')
def urlencode_filter(s):
    """
    Necessary addition to Jinja2 filters, to escape chars for in url.

    :param s:
    :return:
    """
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    if sys.version_info.major == 2:
        s = urllib.quote_plus(s)
    else:
        s = urllib.parse.quote_plus(s)
    return Markup(s)


@app.route('/treeview/<folderpath:tmp_json>')
def treeview(tmp_json):
    with open(tmp_json, 'r') as f:
        treejson = f.read()

    return render_template('jupyter_embedded.html',
                           treefile=tmp_json,
                           json=treejson,
                           treeview=True)


@app.route('/return_from_embeded_view/<folderpath:treefile>', methods=['POST'])
def shutdown(treefile):
    json_data = request.get_json()

    with open(treefile, 'w') as f:
        f.write(json.dumps(json_data))

    shutdown_server()
    return 'Server shutting down...'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
