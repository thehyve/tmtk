#!/usr/bin/env python3
import os
import sys
from collections import OrderedDict

from flask import Flask, flash, request, redirect, url_for, render_template, \
                  json, Response, send_from_directory
from werkzeug import secure_filename
from werkzeug.routing import BaseConverter, ValidationError

import urllib
from markupsafe import Markup

# from .functions.params import StudyParams, ClinicalParams, ExpressionParams, \
#                                 get_study_id
# from .functions.exceptions import HyveException, HyveIOException
# from .functions.clinical import columns_to_tree, json_to_columns, getchildren, \
#                                get_datafiles, get_column_map_file, \
#                                add_to_column_file, get_word_map
# from .functions.feedback import get_feedback_dict, merge_feedback_dicts
# from .functions.highdim import subject_sample_to_tree, get_subject_sample_map
#

from .common import get_feedback_dict
from .jstreecontrol import study_to_concept_tree
from tmtk.study import Study
from flask import g


STUDIES_FOLDER = 'studies'
ALLOWED_EXTENSIONS = ['txt', 'tsv']

# See if the application is run from an executable.
if sys.platform == 'win32' and (hasattr(sys, 'frozen') or hasattr(sys, 'importers')):
    path = os.path.dirname(sys.executable)
    app = Flask(__name__,
                static_folder=os.path.join(path, 'static'),
                template_folder=os.path.join(path, 'templates')
                )

# See if the application is run from inside a .app (MacOSX)
elif sys.platform == 'darwin' and (hasattr(sys, 'frozen') or hasattr(sys, 'importers')):
    path = os.path.dirname(os.path.realpath(__file__))
    pos = path.rfind('lib/')
    path = path[:pos]
    app = Flask(__name__,
                static_folder=os.path.join(path, 'static'),
                template_folder=os.path.join(path, 'templates')
                )
else:
    app = Flask(__name__)

app.secret_key = 'not_so_secret'

app.jinja_env.add_extension("jinja2.ext.do")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.filters['path_join'] = lambda paths: os.path.join(*paths)


def get_study_object(study_params):
    """
    Load study into memory the first time, it will be shared through flask.g space.
    :param study_params: path to study.params file.
    :return: tmtk.Study object
    """
    study_object = g.get('study_object', None)
    if not study_object:
        g.study_object = Study(study_params)
        study_object = g.study_object
    return study_object


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

if not os.path.isdir(STUDIES_FOLDER):
    os.mkdir(STUDIES_FOLDER)

possible_datatypes = ['study', 'clinical', 'expression']


@app.template_filter('urlencode')
def urlencode_filter(s):
    ''' Necessary addition to Jinja2 filters, to escape chars for in url '''
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    if sys.version_info.major == 2:
        s = urllib.quote_plus(s)
    else:
        s = urllib.parse.quote_plus(s)
    return Markup(s)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    default_folder = request.cookies.get('default_folder')
    if default_folder:
        if default_folder.endswith(':/'):
            default_folder = default_folder[:-1]+'\\'
            default_folder = urlencode_filter(default_folder)
        return redirect(url_for('studies_overview', studiesfolder=default_folder))
    else:
        studiesfolder = os.path.abspath(STUDIES_FOLDER)
        studiesfolder = studiesfolder.strip('/')
        return redirect(url_for('studies_overview', studiesfolder=studiesfolder))


@app.route('/folder/create/', defaults={'studiesfolder': '/'}, methods=['POST'])
@app.route('/folder/<folderpath:studiesfolder>/create/', methods=['POST'])
def create_folder(studiesfolder):
    if 'foldername' in request.form:
        foldername = os.path.join(studiesfolder,
                                  request.form['foldername'])
        if not os.path.exists(foldername):
            # TODO handle case where no permission to create folder
            os.mkdir(foldername)

    return redirect(url_for('studies_overview', studiesfolder=studiesfolder))


@app.route('/folder/', defaults={'studiesfolder': '/'})
@app.route('/folder/<folderpath:studiesfolder>/')
def studies_overview(studiesfolder):
    studies = {}

    for file in os.listdir(studiesfolder):
        filepath = os.path.join(studiesfolder, file)
        if os.path.isdir(filepath) and not file.startswith('.'):
            studies[file] = {'type': 'folder'}
            study_params_file = os.path.join(filepath, 'study.params')
            if os.path.exists(study_params_file):
                studies[file]['type'] = 'study'
    ordered_studies = OrderedDict(sorted(studies.items(), key=lambda x: x[0].lower()))

    rootfolder = False
    parentfolder = ''
    if studiesfolder == '/':
        rootfolder = True
    elif studiesfolder.endswith(':/'):  # Converted to have one / instead of \\
        rootfolder = True
        studiesfolder = studiesfolder[:-1]+'\\'
        studiesfolder = urlencode_filter(studiesfolder)
    else:
        parentfolder = os.path.abspath(os.path.join(studiesfolder, os.pardir))
        if parentfolder.endswith(':\\'):
            parentfolder = urlencode_filter(parentfolder)

    return render_template('studiesoverview.html',
                           studiesfolder=studiesfolder,
                           parentfolder=parentfolder,
                           rootfolder=rootfolder,
                           studies=ordered_studies)


@app.route('/folder/s/<study>/', defaults={'studiesfolder': ''})
@app.route('/folder/<folderpath:studiesfolder>/s/<study>/')
def study_page(studiesfolder, study):

    study_object = get_study_object(os.path.join(studiesfolder, study, 'study.params'))

    paramsdict = {}

    # TODO this is all hacky, should be made more flexible, view should be reconsidered
    # for key, params_file in study_object.Params.__dict__.items():
    #     if params_file.datatype not in possible_datatypes:
    #         continue
    #
    #     paramsfile = params_file.path
    #     datatype = params_file.datatype
    #     paramsdict[params_file.datatype] = {}
    #     feedback = get_feedback_dict()
    #
    #     if os.path.exists(paramsfile):
    #         paramsdict[datatype]['exists'] = True
    #         if datatype == 'study':
    #             paramsobject = study_object.find_params_for_datatype('study')[0]
    #         if datatype == 'clinical':
    #             paramsobject = study_object.find_params_for_datatype('clinical')[0]
    #         # elif datatype == 'expression':
    #         #     paramsobject = ExpressionParams(paramsfile)
    #         else:
    #             feedback['errors'].append('Params file {} not supported'.format(paramsfile))
    #     else:
    #         paramsdict[params_file.datatype]['exists'] = False
    #         feedback['infos'].append('No {} found'.format(datatype+'.params'))
    #
    #     params = {}
    #     docslink = ''
    #
    #     try:  # ???
    #         paramsobject
    #     except NameError:
    #         pass
    #     else:
    #         # params = paramsobject.__dict__
    #         # get all upper cased params from param object
    #         params = {key: value for (key, value) in paramsobject.__dict__.items() if key.isupper()}
    #         docslink = paramsobject.docslink
    #         # params_feedback = paramsobject.get_feedback()
    #         # feedback = merge_feedback_dicts(feedback, params_feedback)
    #         feedback = {'feedback': 'THIS VIEW SHOULD BE DEPRECATED'}
    #         params = OrderedDict(sorted(params.items(), key=lambda x: x[0].lower()))

    for datatype in possible_datatypes:
        paramsdict[datatype] = {}
        # get only first params encoutered as multiple are not supported
        paramsobject = study_object.find_params_for_datatype(datatype)[0]
        params = {key: value for (key, value) in paramsobject.__dict__.items() if key.isupper()}
        docslink = paramsobject.docslink
        params = OrderedDict(sorted(params.items(), key=lambda x: x[0].lower()))
        feedback = {'feedback': 'THIS VIEW SHOULD BE DEPRECATED'}

        if paramsobject.is_viable():
            paramsdict[datatype]['exists'] = True
        paramsdict[datatype]['params'] = params
        paramsdict[datatype]['feedback'] = feedback
        paramsdict[datatype]['docslink'] = docslink

    return render_template('studypage.html',
                           studiesfolder=studiesfolder,
                           study=study,
                           paramsdict=paramsdict,
                           possible_datatypes=possible_datatypes)


@app.route('/folder/<folderpath:studiesfolder>/set_default/', methods=["GET"])
def set_default_folder(studiesfolder):
    feedback = "Saved "+studiesfolder
    response = app.make_response((json.jsonify(feedback=feedback), 200))
    response.set_cookie('default_folder', value=studiesfolder)
    return response


@app.route('/folder/<folderpath:studiesfolder>/s/<study>/clinical/create/')
def create_mapping_file(studiesfolder, study):
    columnmappingfile = 'COLUMN_MAP_FILE'
    wordmappingfile = 'WORD_MAP_FILE'

    mappingfile = request.args['variable']

    if mappingfile not in [columnmappingfile, wordmappingfile]:
        return

    studyid = get_study_id(studiesfolder, study)

    datatypepath = os.path.join(studiesfolder, study, 'clinical')
    if not os.path.exists(datatypepath):
        os.mkdir(datatypepath)

    mappingfilename = studyid+'_'+mappingfile+'.tsv'
    mappingfilepath = os.path.join(datatypepath, mappingfilename)
    if not os.path.exists(mappingfilepath):
        with open(mappingfilepath, "w+") as handle:
            tree = {}
            if mappingfile == columnmappingfile:
                mappingfiledata, feedback = json_to_columns(tree=tree)
            elif mappingfile == wordmappingfile:
                mappingfiledata = get_word_map()
            handle.write(mappingfiledata)

    return json.jsonify(mappingfilename=mappingfilename)


@app.route(('/folder/<folderpath:studiesfolder>/s/<study>/params/<datatype>/'
            'create/'))
def create_params(studiesfolder, study, datatype):
    feedback = get_feedback_dict()
    paramsfile = os.path.join(studiesfolder, study, datatype+'.params')

    if not os.path.exists(paramsfile):
        with open(paramsfile, "w+"):
            flash('Successfully created {}.'.format(
                os.path.basename(paramsfile)))
    if datatype != 'study':
        datatypepath = os.path.join(studiesfolder, study, datatype)
        if not os.path.exists(datatypepath):
            os.mkdir(datatypepath)

    return redirect(url_for('edit_params',
                            studiesfolder=studiesfolder,
                            study=study,
                            datatype=datatype))


@app.route('/folder/<folderpath:studiesfolder>/s/<study>/params/<datatype>/',
           methods=['GET', 'POST'])
def edit_params(studiesfolder, study, datatype):
    feedback = get_feedback_dict()
    paramsfile = os.path.join(studiesfolder, study, datatype+'.params')

    if request.method == 'POST':
        if os.path.exists(paramsfile):
            if datatype == 'study':
                paramsobject = StudyParams(paramsfile)
            elif datatype == 'clinical':
                paramsobject = ClinicalParams(paramsfile)
            elif datatype == 'expression':
                paramsobject = ExpressionParams(paramsfile)
            else:
                flash('Params file {} not supported'.
                      format(os.path.basename(paramsfile)), 'error')
        else:
            flash('Params file {} does not exist'.
                  format(os.path.basename(paramsfile)), 'error')

        try:
            paramsobject
        except NameError:
            pass
        else:
            for variable in request.form:
                paramsobject.update_variable(variable,
                                             request.form[variable])
            app.logger.debug(paramsobject.get_variables())
            paramsobject.save_to_file()
            feedback = paramsobject.get_feedback()

    if os.path.exists(paramsfile):
        if datatype == 'study':
            paramsobject = StudyParams(paramsfile)
        elif datatype == 'clinical':
            paramsobject = ClinicalParams(paramsfile)
        elif datatype == 'expression':
            paramsobject = ExpressionParams(paramsfile)
        else:
            flash('Params file {} not supported'.
                  format(os.path.basename(paramsfile)), 'error')
    else:
        flash('Params file {} does not exist'.
              format(os.path.basename(paramsfile)), 'error')

    params = {}
    variables = {}
    try:
        paramsobject
    except NameError:
        pass
    else:
        variables = paramsobject.get_possible_variables()
        params = paramsobject.get_variables()

        for variable in variables:
            if variable in params:
                    variables[variable]['value'] = params[variable]

        params_feedback = paramsobject.get_feedback()
        feedback = merge_feedback_dicts(feedback, params_feedback)

    variables = OrderedDict(sorted(variables.items(),
                                   key=lambda x: x[0].lower()))

    return render_template('params.html',
                           studiesfolder=studiesfolder,
                           study=study,
                           datatype=datatype,
                           variables=variables,
                           feedback=feedback)


@app.route('/folder/<folderpath:studiesfolder>/s/<study>/tree/')
def edit_tree(studiesfolder, study):
    # columnsfile = get_column_map_file(studiesfolder, study)
    # if columnsfile is not None:
    #     tree_array = columns_to_tree(columnsfile)
    #     clinical_datafiles = get_datafiles(columnsfile)
    # else:
    #     tree_array = []
    #     clinical_datafiles = []
    #
    # # Get expression subject sample mapping and paths in there
    # subject_sample_map = get_subject_sample_map(studiesfolder,
    #                                             study,
    #                                             'expression')
    # if subject_sample_map is not None:
    #     tree_array = subject_sample_to_tree(subject_sample_map, tree_array)
    #
    # concept_tree_json_string = json.dumps(tree_array)

    study_object = get_study_object(os.path.join(studiesfolder, study, 'study.params'))

    concept_tree_json_string = study_to_concept_tree(study_object)

    clinical_datafiles = study_object.Clinical.ColumnMapping.included_datafiles

    return render_template('tree.html',
                           studiesfolder=studiesfolder,
                           clinicaldatafiles=clinical_datafiles,
                           study=study,
                           json=concept_tree_json_string)


@app.route('/folder/<folderpath:studiesfolder>/s/<study>/tree/add/', methods=['POST'])
def add_datafile(studiesfolder, study):
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        datafilepath = os.path.join(studiesfolder, study, 'clinical', filename)
        if not os.path.exists(datafilepath):
            file.save(datafilepath)
            columnmappingfilepath = get_column_map_file(studiesfolder, study)
            if columnmappingfilepath is not None:
                add_to_column_file(datafilepath, columnmappingfilepath)
                flash('Data file \'{}\' added to column mapping file'.format(
                    os.path.basename(datafilepath)))
            else:
                flash('No column mapping file found', 'error')
        else:
            flash('Data file \'{}\' already exists'.format(
                os.path.basename(datafilepath)), 'error')
    else:
        flash('File type not allowed', 'error')

    return redirect(url_for('edit_tree',
                            studiesfolder=studiesfolder,
                            study=study))


@app.route('/folder/<folderpath:studiesfolder>/s/<study>/tree/save_columnsfile/',
           methods=['POST'])
def save_columnsfile(studiesfolder, study):
    feedback = get_feedback_dict()

    json_data = request.get_json()
    tree, feedback_json_to_columns = json_to_columns(tree)

    feedback = merge_feedback_dicts(feedback, feedback_json_to_columns)

    columnsfile = get_column_map_file(studiesfolder, study)
    if columnsfile is not None:
        columnmappingfile = open(columnsfile, 'w')
        columnmappingfile.write(tree)
        columnmappingfile.close()

        feedback['infos'].append('Saved column mapping file \'{}\'.'.format(
            os.path.split(columnsfile)[1]))
    else:
        feedback['errors'].append('No params file loaded')

    return json.jsonify(feedback=feedback)


@app.route('/treeview/<folderpath:tmp_json>')
def treeview(tmp_json):

    with open(tmp_json, 'r') as f:
        treejson = f.read()

    # study_object = get_study_object(os.path.join(studiesfolder, study, 'study.params'))

    # concept_tree_json_string = study_to_concept_tree(study_object)
    #
    # clinical_datafiles = study_object.Clinical.ColumnMapping.included_datafiles
    clinical_datafiles = ['foo', 'bar', 'baz']

    return render_template('jupyter_embedded.html',
                           studiesfolder=tmp_json,
                           clinicaldatafiles=clinical_datafiles,
                           study='This content has to be removed.',
                           json=treejson,
                           treeview=True)


@app.route('/return_from_embeded_view/<folderpath:mapfile>', methods=['POST'])
def shutdown(mapfile):
    json_data = request.get_json()

    with open(mapfile, 'w') as f:
        f.write(json.dumps(json_data))

    shutdown_server()
    return 'Server shutting down...'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.errorhandler(404)
def errorhandler(e):
    code = 404
    return render_template('error.html', error=str(e), code=code), code


@app.errorhandler(403)
def errorhandler(e):
    code = 403
    return render_template('error.html', error=str(e), code=code), code


@app.errorhandler(405)
def errorhandler(e):
    code = 405
    return render_template('error.html', error=str(e), code=code), code


@app.errorhandler(410)
def errorhandler(e):
    code = 410
    return render_template('error.html', error=str(e), code=code), code


@app.errorhandler(500)
def errorhandler(e):
    code = 500
    return render_template('error.html', error=str(e), code=code), code

if __name__ == '__main__':
    app.debug = True
    app.run()
