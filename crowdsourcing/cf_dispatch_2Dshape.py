import requests
from queue import Queue

import os
import time

os.environ['domain'] = '2Dshape'

from main.core.utils import get_confirmation_code
from main.core.data import get_chat_db, get_dispatch_semaphore, set_dispatch_semaphore
from main.core.const import TASK_ID, ROLE, AGENT, USER
from pymongo import DESCENDING
from server_config import SERVER_HOST, SERVER_PORT
from crowdflower import CF_API_ENDPOINT, INSTRUCTOR_JOBID, PAINTER_JOBID, API_KEY

instructor_config = {
    "id": INSTRUCTOR_JOBID,
    "title": "2Dshape_instructor_job",
    'instruction_path': "main/static/cf_2Dshape_user.html",
}
painter_config = {
    "id": PAINTER_JOBID,
    "title": "2Dshape_painter_job",
    'instruction_path': "main/static/cf_2Dshape_agent.html",
}


class JobManager:
    def __init__(self, role):
        self.api_key = API_KEY
        self.role = role
        assert self.role in ['instructor', 'painter']
        self.config = {'instructor': instructor_config, 'painter': painter_config}[self.role]
        self.job_id = self.config['id']
        self.taskidQueue = Queue()
        self.dispatch_size = 2
        self.role_mapping = {'instructor': 'user', 'painter': 'agent'}
        self.setup()

    def setup(self):
        self.update_title(self.config['title'])
        self.set_job_cml()
        self.update_instruction()
        self.set_judgements_per_rows()
        self.set_automatic_launch()

    def update_title(self, new_title):
        url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
        data = {'job[title]': new_title}
        r = requests.put(url, data=data)
        r.raise_for_status()

    def update_instruction(self):
        url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
        data = {'job[instructions]': '<h1>Welcome!</h1>'}
        r = requests.put(url, data=data)
        r.raise_for_status()
        # with open(self.config['instruction_path'], 'r') as f:
        #     instruction = f.read()
        #     url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
        #     data = {'job[instructions]': instruction}
        #     r = requests.put(url, data=data)
        #     r.raise_for_status()

    def set_job_cml(self):
        with open(self.config['instruction_path'], 'r') as f:
            instruction = f.read()
            url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
            cml = """<div class="html-element-wrapper">
            <a class="clicked validates-clicked" href="{{taskurl}}" target="_blank">Click Here to go to the task</a>
            </div>
            <cml:text label="Confirmation Code" data-validates-regex="{{confirmation_code}}$"
            validates="required ss-required regex" data-validates-regex-message="Please copy and paste the code here that can be found at the end of the Survey"
            default="Enter here..."
            instructions="Enter confirmation code in this field after completing"></cml:text>
            """
            data = {'job[cml]': instruction + '\n\n' + cml}
            r = requests.put(url, data=data)
            r.raise_for_status()

    def set_judgements_per_rows(self):
        url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
        data = {'job[max_judgments_per_unit]': '1'}
        r = requests.put(url, data=data)
        r.raise_for_status()

    def add_row(self, taskid):
        self.taskidQueue.put(taskid)
        print("{} job manager added taskid {}".format(self.role, taskid))

    def launch_job(self):
        url = "https://api.crowdflower.com/v1/jobs/{}/orders.json?key={}".format(self.job_id, self.api_key)
        data = {'channels[0]': 'cf_internal', 'debit[units_count]': '{100}'}
        r = requests.post(url, data=data)
        r.raise_for_status()

    def set_automatic_launch(self):
        url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
        data = {'job[auto_order]': 'true'}
        r = requests.put(url, data=data)
        r.raise_for_status()

    def pay_worker_bonus(self, worker_id, amount_in_cents):
        url = (CF_API_ENDPOINT +
               "{job_id}/workers/{worker_id}/bonus.json?key={api_key}".format(
                   job_id=self.job_id, worker_id=worker_id, api_key=self.api_key))
        data = {'amount': amount_in_cents}
        r = requests.post(url, data=data)
        r.raise_for_status()

    def dispatch(self):
        if self.taskidQueue.qsize() >= self.dispatch_size:
            taskids = []
            for i in range(self.dispatch_size):
                taskids.append(self.taskidQueue.get())

            # code = str(int(taskids[0][::-1]) + 12345)
            code = get_confirmation_code(taskids[0])
            url = "https://api.crowdflower.com/v1/jobs/{}/units.json?key={}".format(self.job_id, self.api_key)
            taskurl = '{}:{}/login?role={}&mode=2Dshape&tasks={}'.format(SERVER_HOST, SERVER_PORT,
                                                                         self.role_mapping[self.role],
                                                                         ';'.join(taskids))
            data = {'unit[data][taskurl]': taskurl, 'unit[data][confirmation_code]': code}
            r = requests.post(url, data=data)
            r.raise_for_status()
            print("{} job manager dispatched tasks {}".format(self.role, ', '.join(taskids)))


def fetch_tasks(instructor_jobs, painter_jobs, task_ids):
    db_chat = get_chat_db(is_debug=False)
    for task_id in task_ids:
        task_semaphore = get_dispatch_semaphore(task_id)
        if task_semaphore == 0:
            continue
        last_entry = db_chat.find({TASK_ID: task_id}).sort("timestamp", DESCENDING).limit(1)
        if last_entry.count() == 0:
            instructor_jobs.add_row(task_id)
            set_dispatch_semaphore(task_id, 0)
        else:
            if last_entry[0]['msg'].startswith('#END'):
                continue
            if last_entry[0][ROLE] == AGENT:
                instructor_jobs.add_row(task_id)
            else:
                painter_jobs.add_row(task_id)
            set_dispatch_semaphore(task_id, 0)


if __name__ == '__main__':
    instructor_job_manager = JobManager('instructor')
    painter_job_manager = JobManager('painter')
    while True:
        fetch_tasks(instructor_job_manager, painter_job_manager, ['20000', '20001'])
        instructor_job_manager.dispatch()
        painter_job_manager.dispatch()
        time.sleep(2)
