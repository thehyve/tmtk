import requests
import getpass
from urllib.parse import urlparse
from ..utils import Message, PathError


def get_instance_url(url):
    o = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=o)
    return domain


def login_url(url):
    return get_instance_url(url) + 'accounts/login/'


def json_url(url):
    o = urlparse(url)
    path_items = o.path.split('/')
    if len(path_items) < 4 or path_items[1] != 'trees':
        raise PathError('To get json, input url should study name and version. (e.g. '
                        'http://transmart-arborist.thehyve.nl/trees/study-name/1/~edit/.')

    return '{uri.scheme}://{uri.netloc}{path}'.format(uri=o, path='/'.join(path_items[:4]))


def start_session(url, username):
    client = requests.session()

    auth_url = login_url(url)
    # Retrieve the CSRF token first
    client.get(auth_url)  # sets cookie

    username = username or input("Enter username:")
    password = getpass.getpass('Enter password:')

    login_data = {'login': username,
                  'password': password,
                  'csrfmiddlewaretoken': client.cookies['csrftoken']}
    r = client.post(auth_url, data=login_data, headers={'Referer': auth_url})
    if r.text.find(username) == -1 or not r.status_code == 200:
        raise Exception('Could not login.')
    return client


def get_json_from_baas(url, username=None):
    """
    Get a json file from a Boris as a Service instance.

    :param url: url should study name and version.
        (e.g. http://transmart-arborist.thehyve.nl/trees/study-name/1/~edit/).
    :param username: if no username is given, you will be prompted for one.
    :return: the JSON string from BaaS.
    """
    client = start_session(url, username)
    r = client.get(json_url(url))
    r.raise_for_status()
    return r.text


def publish_to_baas(url, json, study_name, username=None):
    """
    Publishes a tree on a Boris as a Service instance.

    :param url: url to a BaaS instance.
    :param json: the stringified json you want to publish.
    :param study_name: a nice name.
    :param username: if no username is given, you will be prompted for one.
    :return: the url that points to the study you've just uploaded.
    """
    client = start_session(url, username)
    add_study_url = get_instance_url(url) + 'trees/add/'

    while True:
        study_data = {'name': study_name,
                      'json': json,
                      'csrfmiddlewaretoken': client.cookies['csrftoken']}

        r = client.post(add_study_url, data=study_data, headers={'Referer': add_study_url})
        r.raise_for_status()
        if r.url.endswith('trees/add/'):
            print('Study name {!r} is probably taken, '
                  'pick another by setting study_name parameter.'.format(study_name))
            study_name = input('Pick a new name:')
        elif '/trees/' in r.url:
            Message.okay('Study added. You can find it in the BaaS instance.')
            return r.url
