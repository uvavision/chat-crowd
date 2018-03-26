import random
import string

import hashlib
import requests
from crowdsourcing.crowdflower import CF_API_ENDPOINT, INSTRUCTOR_JOBID, PAINTER_JOBID, API_KEY

def randomword(length=8):
    char_set = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return ''.join(random.choice(char_set) for i in range(length))


def notify_worker(job_id, worker_id, message_to_worker):
    url = ('https://api.crowdflower.com/v1/jobs/{job_id}/workers/{worker_id}/notify.json?key={api_key}'.format(
               job_id=job_id, worker_id=worker_id, api_key=API_KEY))
    data = {"message": message_to_worker}
    r = requests.post(url, data=data)
    return r.status_code, r.reason


def send_user_code(worker_id, confirmation_code):
    return notify_worker(INSTRUCTOR_JOBID, worker_id, confirmation_code)


def send_agent_code(worker_id, confirmation_code):
    return notify_worker(PAINTER_JOBID, worker_id, confirmation_code)


def get_confirmation_code(task_id, is_hash=True):
    if is_hash:
        return hashlib.md5((str(task_id)).encode()).hexdigest()
    else:
        return str(int(task_id[::-1]) + 12345)
