import requests
import json
import os.path
import crowdflower
from .. import APP_DATA

API_URL = 'https://api.crowdflower.com/v1/'
API_KEY = "EryJhbCbXnzucFZGo4ih"   # "EryJhbCbXnzucFZGo4ih"
job_id = "1004773"  # chat data agent
CML = open(os.path.join(APP_DATA, 'templates/confirmation.cml')).read()
data_json = os.path.join(APP_DATA, 'cf/data.json')

conn = crowdflower.Connection(api_key=API_KEY, cache='filesystem')

class CF_API_Hook(object):

    def __init__(self, api_key=API_KEY, api_url=API_URL, job_id=None):
        self.api_key = api_key
        self.api_url = api_url
        self.job_id = job_id
        self.headers = {'content-type': 'application/json'}
        self.job_url = ""
        if self.job_id:
            self.job_url = self.api_url + "jobs/{}/".format(self.job_id)

    def create_blank_job(self): # create
        request_url = API_URL + 'jobs.json?key={}'.format(self.api_key)
        res = requests.post(request_url)
        self.job_id = res.json()['id']
        return res

    def create_job(self, title, instructions=None, cml=None):
        request_url = self.api_url + "jobs.json?"
        headers = {'content-type': 'application/json'}
        payload = {
            'key': self.api_key,
            'job': {
                'title': title,
                'instructions': instructions,
                'cml': cml
            }
        }
        res = requests.post(request_url, data=json.dumps(payload), headers=headers)
        self.job_id = res.json()['id']
        self.job_url = self.api_url + "jobs/{}/".format(self.job_id)
        return res

    def set_row_data(self, data, job_id=None): # add data rows to a job
        if not job_id and self.job_id:
            job_id = self.job_id
        else:
            return None
        request_url = self.job_url + "/units.json".format(job_id)
        headers = {'content-type': 'application/json'}
        payload = {
            'key': self.api_key,
            'unit': {
                'data': data # a column/value json
            }
        }
        res = requests.post(request_url, data=json.dumps(payload), headers=headers)
        return res

    def set_row_json(self, data_json): # add data rows to a job
        request_url = self.job_url + "/upload.json?key={api_key}&force=true".format(api_key=self.api_key)
        headers = {'content-type': 'application/json'}
        res = requests.post(request_url, data=open(data_json), headers=headers)
        return res

    def get_row_by_job(self):
        request_url = self.job_url + "/units.json?key={api_key}&page=1".format(api_key=self.api_key)
        print(request_url)
        res = requests.get(request_url)
        return res

    def pay_bonus(self, job_id, worker_id, amount_in_cents):
        path = 'jobs/{}/workers/{}/bonus.json'.format(job_id, worker_id)
        conn.create_request(path, {'amount': amount_in_cents})

    def notify_worker(self, job_id, worker_id, message_to_worker):
        path = 'jobs/{}/workers/{}/notify.json'.format(job_id, worker_id)
        conn.create_request(path, {'message': message_to_worker})

    def launch_internal_channel(self):
        request_url = self.job_url + "/orders.json"
        # "channels[0]=cf_internal&debit[units_count]={100}"
        headers = {'content-type': 'application/json'}
        payload = {
            'key': self.api_key,
            'channels': ['cf_internal'],
            'debit': {
                'units_count': 2
            }
        }
        res = requests.post(request_url, data=json.dumps(payload), headers=headers)
        return res


if __name__ == '__main__':
    pass
    cf = CF_API_Hook() # job_id='1187386'
    # data = {"task_url": "woz-chat.mybluemix.net/login?taskid=001&role=agent", "task_id": "001", "role": "agent"}
    # res = cf.create_job('test', 'desc-test', CML)
    # print(cf.job_id)
    # res = cf.set_row_json(data_json)
    # res = cf.get_row_by_job()
    # print(res.json())
    # res = cf.launch_internal_channel()
    # print(res.json())
    # curl -X GET "https://api.crowdflower.com/v1/jobs/1187345/units.json?key=EryJhbCbXnzucFZGo4ih&page=1"
