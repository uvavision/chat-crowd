import crowdflower
from crowdflower.serialization import rails_params
import json
import os
import sys
import urllib
from .. import APP_DATA, APP_URL
from ..core.utils import randomword

CF_DIR = os.path.join(APP_DATA, 'cf')
CF_JSON = os.path.join(CF_DIR, 'cf.json')
cf_data = json.loads(open(CF_JSON, 'rb').read())
crowd_meta = cf_data['task']
end_point_url = cf_data['account'][0]['endpoint_url']
API_KEY = cf_data['account'][0]['key']

JOB_ID = 1192310
JOB_TITLE = ""
contributor_id = '43828552'
role = ''
TEMPLATE_DIR = os.path.join(APP_DATA, 'templates')
INSTRUCTION_HTML = os.path.join(TEMPLATE_DIR, 'instruction_{}.html'.format(role))
INSTRUCTION_CML = os.path.join(TEMPLATE_DIR, 'instruction_{}.cml'.format(role))


def get_taskurl(taskid, role, is_debug=False):
    url_domain = APP_URL
    # url_str = '{0}taskid={1}&role={2}'.format(url_domain, taskid, role)
    if is_debug:
        params = {'taskid': taskid, 'role': role, 'debug': 1}
    else:
        params = {'taskid': taskid, 'role': role}
    url_str = url_domain + urllib.urlencode(params)
    return url_str


def _generate_cf_task_json(begin, end, out_json):
    # localhost:port/login?username=adam&taskid=34567&role=agent
    fp = open(out_json, 'wb')
    cols = ['ID', 'TASK_URL', 'TASK_ID', 'ROLE', 'USERNAME', 'NOTE']
    for i in range(begin, end + 1, 2):
        for role in ['agent', 'user']:
            d = {}
            task_id = randomword(8) + '-' + str(i)
            d['task_id'] = task_id
            d['role'] = role
            d['task_url'] = get_taskurl(task_id, role)
            d['confirmation'] = task_id[::-1]
            fp.write(json.dumps(d) + '\n')


def calculate_reward(n, role, bonus=0):
    if n == 0:
        return 0
    key = 'base_reward_' + role
    if role == 'user':
        return crowd_meta[key] + bonus
    elif role == 'agent':
        a = n - 1
        return crowd_meta[key] * n + 0.1 * (a + a**2)//2 + bonus
    return 0



def generate_cf_task_json(begin, end):
    json_fn = 'cf_chat_tasks_{}_{}.json'.format(begin, end)
    fn = os.path.join(CF_DIR, json_fn)
    print('writing to', fn)
    _generate_cf_task_json(begin, end, fn)


class CF_API_Hook(object):

    def __init__(self, api_key=API_KEY, job_id=None):
        self.api_key = api_key
        self.job_id = job_id
        self.conn = crowdflower.Connection(api_key=api_key)
        self.job = None

    def _find_job(self):
        return self.job

    def get_job_by_id(self, job_id):
        for job in self.conn.jobs():
            if job_id == job.id:
                self.job = job
                return job

    def find_job_tag(self, job_tag):
        for job in conn.jobs():
            if job_tag in job.tags:
                self.job = job
                return job

    def new_job(self, data, d_para=None):
        self.job = self.conn.upload(data)  # add data
        res = self.job.update(d_para)

    def add_data(self, data):
        self.job.upload(data)  # [{}, {}]

    def launch(self, units_count, channels=('on_demand',)):
        self.job.launch(units_count, channels)
        print >> sys.stderr, 'Launched Job[%d]' % self.job_id

    def ping(self):  # get the status
        print self.job.ping()

    def results(self):
        job = _find_job()
        try:
            for judgment in job.judgments:
                print '\t'.join([judgment['label'], judgment['text']])
        except CrowdFlowerError, exc:
            # explain HTTP 202 Accepted response
            if exc.response.status_code == 202:
                print >> sys.stderr, 'Try again in a moment', exc

    def download(self):
        for judgment in job.judgments:
            print json.dumps(judgment)

    def delete(self):
        print >> sys.stderr, 'Deleting Job[%d]' % self.job_id
        self.job.delete()

    def delete_job_by_id(self, job_id):
        job = self.get_job_by_id(job_id)
        job.delete()

    def cancel(self):
        self._connection.request('/jobs/%s/cancel' % self.job_id)

    def pause(self):
        self._connection.request('/jobs/%s/pause' % self.job_id)

    def resume(self):
        self._connection.request('/jobs/%s/resume' % self.job_id)

    def update(self, d_prop):
        return self.job.update(d_prop)

    def request(self, path, method, params):
        res = self.conn.request('/jobs/%s/gold' % self.id, method='PUT', params=params)
        self.conn.request('/jobs/%s/units/%s' % (self.id, unit_id), method='DELETE')
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'unit': {'data': unit}})
        res = self._connection.request('/jobs/%s/units' % self.id, method='POST', headers=headers, data=data)

    def set_bonus(self, amount_in_cents, job_id, worker_id):
        '''
        curl -X POST --data-urlencode "amount={amount_in_cents}" https://api.crowdflower.com/v1/jobs/{job_id}/workers/{worker_id}/bonus.json?key={api_key}
        '''
        # data = rails_params(dict(channels=channels, debit=dict(units_count=units_count)))
        data = rails_params(dict(amount=amount_in_cents))
        res = self._connection.request('/jobs/%s/orders/workers/%s/bonus' % (job_id, worker_id), method='POST', params=data)
        # self._cache_flush('properties')
        return res

        '''
        curl -X POST -d "channels[0]=on_demand&debit[units_count]={100}" https://api.crowdflower.com/v1/jobs/{job_id}/orders.json?key={api_key}

        channels = list(channels)
        data = rails_params(dict(channels=channels, debit=dict(units_count=units_count)))
        res = self._connection.request('/jobs/%s/orders' % self.id, method='POST', params=data)
        self._cache_flush('properties')
        '''

    def notify_contributor(self, worker_id, job_id, message_to_worker, amount_in_cents):
        '''
        curl -X POST --data-urlencode "message={message_to_worker}" https://api.crowdflower.com/v1/jobs/{job_id}/workers/{worker_id}/notify.json?key={api_key}
        '''
        data = rails_params(dict(message=amount_in_cents))
        res = self._connection.request('/jobs/%s/orders/workers/%s/bonus' % (job_id, worker_id), method='POST', params=data)
        return res


def load_data(fn):
    data = []
    with open(fn) as f:
        for line in f:
            data.append(json.loads(line))
    return data


def new_job(role, data):
    cf = CF_API_Hook()
    cml_content = open(os.path.join(TEMPLATE_DIR, 'confirmation.cml')).read()
    inst_txt = os.path.join(TEMPLATE_DIR, '_instructions_{}.txt'.format(role))
    inst_cml = os.path.join(TEMPLATE_DIR, 'instruction_{}.cml'.format(role))
    job = cf.conn.upload(data)
    inst_content = open(inst_txt, 'rb').read()
    d_para = {
        'title': 'Chat as a {} of Online Service (Rental Apartments)'.format(role),
        'included_countries': ['US', 'GB'],
        'payment_cents': 1,
        'judgments_per_unit': 1,
        'units_per_assignment': 1,
        'instructions': inst_content,
        'cml': cml_content
        # 'options': {'front_load': 1, # quiz mode = 1; turn off with 0}
    }
    res = job.update(d_para)
    if 'errors' in res:
        print(res['errors'])
        exit()
    return job


if __name__ == '__main__':
    cf = CF_API_Hook()
    # job = cf.get_job_by_id(JOB_ID)
    data_user = [{"role": "user", "task_url": "http://woz.mybluemix.net/login?role=user&taskid=XOj8GKqL-1", "task_id": "XOj8GKqL-1"}]
    job = new_job('user', data_user)
    # print(job.id)
    # job_id_done = 1192485
    # job = cf.get_job_by_id(JOB_ID)
    print(job.id)
    # cml_content = open(os.path.join(curr_path, 'templates/confirmation.cml')).read()
    # cml_content = open(INSTRUCTION_AGENT_CML, 'rb').read()
    # ins_content = open(INSTRUCTION_AGENT_HTML, 'rb').read()
    # res = job.update({'cml': cml_content})
    # res = job.update({'instructions': 'ins_content'})
    # print(res)
    # job.download_csv(os.path.join(curr_path, 'data/results.csv'))
    # job.launch(2, ('cf_internal'))
    # job_new = job.copy()
    # print(job_new.id)
    # data = load_data(os.path.join(curr_path, 'data/data.json'))
    # job_new.upload_unit({})
