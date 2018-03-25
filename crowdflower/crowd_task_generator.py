import hashlib
import urllib
from server_config import SERVER_HOST, SERVER_PORT

APP_URL = "{}:{}/login?".format(SERVER_HOST, SERVER_PORT)

def get_confirmation_code(task_id, is_hash=True):
    if is_hash:
        return hashlib.md5((str(task_id)).encode()).hexdigest()
    else:
        return str(int(task_id[::-1]) + 12345)


def get_task_url(mode, role, tasks, url_domain=APP_URL):
    '''
    TODO: move domain task url generation here?
    '''
    params = {'tasks': tasks, 'role': role, 'mode': mode}
    url_str = url_domain + urllib.urlencode(params)
    return url_str
