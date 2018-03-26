import hashlib
import urllib
from .server_config import SERVER_HOST, SERVER_PORT

APP_URL = "{}:{}/login?".format(SERVER_HOST, SERVER_PORT)


def get_task_url(mode, role, tasks, url_domain=APP_URL):
    '''
    TODO: move domain task url generation here?
    '''
    params = {'tasks': tasks, 'role': role, 'mode': mode}
    url_str = url_domain + urllib.urlencode(params)
    return url_str
