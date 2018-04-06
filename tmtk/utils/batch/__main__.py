from ._wrapper import TransmartBatch, ConfigurationError
from ...study import Study

import sys
import click
import os

get_input = input


def choose_property_files():
    try:
        params_ = [p.name for p in list(TransmartBatch().get_property_files())]
    except ConfigurationError:
        params_ = []
    return click.Choice(params_)


def _find_study_params_in_parent(path):
    """ Recurse through parents to look for a study.params file """
    study_params = os.path.join(path.rsplit(os.sep, 2)[0], 'study.params')

    if os.path.exists(study_params):
        return study_params
    elif len(study_params.split(os.sep)) > 1:
        return _find_study_params_in_parent(study_params)


def list_connection_files(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo("Property files in $TMBATCH_HOME:")
    try:
        for p in TransmartBatch().get_property_files():
            click.echo("  {} ({}):".format(p.name, p.path))
            click.echo("  ..batch.jdbc.driver={}".format(p.driver))
            click.echo("  ..batch.jdbc.url={}".format(p.url))
            click.echo("  ..batch.jdbc.user={}".format(p.user))
            click.echo("  ..batch.jdbc.password={}\n".format(p.password))

    except ConfigurationError:
        click.echo("transmart-batch home directory not set.")
        pass

    ctx.exit()


def run_batch_cmd(params=None, connection_file=None, validate=False, log=None, no_log=False):
    if params:
        if not params.endswith('.params'):
            click.echo('Aborted: {!r} is not a .params file.'.format(os.path.basename(params)))
            sys.exit(1)

        params = os.path.abspath(params)
        if params.endswith('study.params'):
            study_params = params
            is_study_job = True
        else:
            study_params = _find_study_params_in_parent(params)
            is_study_job = False
    else:
        return

    if not study_params:
        sys.exit('Aborted: study.params not found in parent directories. Is params part of study?')

    study = Study(study_params)

    if validate:
        study.validate_all(5)
        if connection_file and get_input('Continue loading y/n?').lower() != 'y':
            return

    if connection_file:
        log = log or not no_log
        if is_study_job:
            getattr(study.load_to, connection_file)(log=log, non_html=True)
        else:
            item_to_load = study.get_object_from_params_path(params)
            getattr(item_to_load.load_to, connection_file)(log=log, non_html=True)


@click.command()
@click.option('-c', '--connection-file', type=choose_property_files(),
              help='Set this to a `batchdb.properties` file to load to a transmart database.')
@click.option('-p', '--params', type=click.Path(),
              help='Params file to load or validate, a complete study or an individual data set.')
@click.option('--validate', default=False, is_flag=True, help='Set this to run the validator.')
@click.option('--log', type=click.Path(),
              help='Write log to this file. Defaults to `transmart-batch.log` in the params folder.')
@click.option('--no-log', default=False, is_flag=True, help='Do not write a log.')
@click.option('--list', is_flag=True, callback=list_connection_files, expose_value=False,
              is_eager=True, help="shows list of available connection files ")
@click.version_option(prog_name="tmtk's transmart-batch wrapper")
def run_batch(params=None, connection_file=None, validate=False, log=None, no_log=False):
    run_batch_cmd(params, connection_file, validate, log, no_log)


__cmd_doc = """\
    A wrapper for starting transmart-batch or the validator. Requires $TMBATCH_HOME environment variable
    to be set, and a path to the transmart-batch parameter file to load.

    \b
    $  --param or -p is required to interact with data, yet requires:
    $  --validate and -c can be used to validate the data and/or load to a database.

    To load data to transmart, correct property files have to be present in $TMBATCH_HOME.
    These files have to end with `.properties`. It is recommended to use a descriptive prefix
    as that will be used to identify it (e.g. `production.properties`).

    The contents of these files typically look something like:

    \b
    For PostgreSQL:
      batch.jdbc.driver=org.postgresql.Driver
      batch.jdbc.url=jdbc:postgresql://localhost:5432/transmart
      batch.jdbc.user=tm_cz
      batch.jdbc.password=tm_cz
    \b
    or for Oracle:
      batch.jdbc.driver=oracle.jdbc.driver.OracleDriver
      batch.jdbc.url=jdbc:oracle:thin:@localhost:1521:ORCL
      batch.jdbc.user=tm_cz
      batch.jdbc.password=tm_cz

    For more info, visit www.github.com/thehyve/transmart-batch.
    """


run_batch_cmd.__doc__ = run_batch.__doc__ = __cmd_doc


if __name__ == "__main__":
    run_batch()

