import threading
import atexit
from flask import Flask
from flask import request
from flask import jsonify
import json
import requests
from queue import Queue

instructor_config = {
    "id": 1247844,
    "title": "2Dshape_instructor_job",
    'instruction_path': "../main/static/cf_2Dshape_user.html",
}
painter_config = {
    "id": 1247845,
    "title": "2Dshape_painter_job",
    'instruction_path': "../main/static/cf_2Dshape_agent.html",
}

class JobManager:
    def __init__(self, role):
        self.api_key = 'guEi5sp-kQsXArgiESzj'
        self.role = role
        assert self.role in ['instructor', 'painter']
        self.config = {'instructor': instructor_config, 'painter': painter_config}[self.role]
        self.job_id = self.config['id']
        self.taskidQueue = Queue()
        self.dispatch_size = 2
        self.role_mapping = {'instructor': 'user', 'painter': 'agent'}

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
            <cml:text label="Confirmation Code" data-validates-regex="{{confirmation_code}}" 
            validates="required ss-required regex" data-validates-regex-message="Please copy and paste the code here that can be found at the end of the Survey" 
            default="Enter here..." 
            instructions="Enter Survey code in this field after completing"></cml:text>
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

    def dispatch(self):
        if self.taskidQueue.qsize() >= self.dispatch_size:
            taskids = []
            for i in range(self.dispatch_size):
                taskids.append(self.taskidQueue.get())

            code = str(int(taskids[0][::-1]) + 12345)
            url = "https://api.crowdflower.com/v1/jobs/{}/units.json?key={}".format(self.job_id, self.api_key)
            taskurl = 'http://deep.cs.virginia.edu:8080/login?role={}&mode=2Dshape&tasks={}'.format(
                self.role_mapping[self.role], ';'.join(taskids))
            data = {'unit[data][taskurl]': taskurl, 'unit[data][confirmation_code]': code}
            r = requests.post(url, data=data)
            r.raise_for_status()
            print("{} job manager dispatched tasks {}".format(self.role, ', '.join(taskids)))


POOL_TIME = 5 #Seconds
yourThread = threading.Thread()

instructor_job_manager = JobManager('instructor')
painter_job_manager = JobManager('painter')

instructor_job_manager.setup()
painter_job_manager.setup()

for i in range(10):
    taskid = str(12345 + i)
    instructor_job_manager.add_row(taskid)

# TODO
# set Max Judgments per Contributor in Quality Control to 2
# instructor_job_manager.launch_job()
# painter_job_manager.launch_job()

# https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask
def create_app():
    app = Flask(__name__)

    def interrupt():
        global yourThread
        yourThread.cancel()

    def job_manager_dispatch():
        global instructor_job_manager
        global painter_job_manager
        global yourThread
        instructor_job_manager.dispatch()
        painter_job_manager.dispatch()
        # Set the next thread to happen
        yourThread = threading.Timer(POOL_TIME, job_manager_dispatch, ())
        yourThread.start()

    def job_manager_dispatch_start():
        # Do initialisation stuff here
        global yourThread
        # Create your thread
        yourThread = threading.Timer(POOL_TIME, job_manager_dispatch, ())
        yourThread.start()

    # Initiate
    job_manager_dispatch_start()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app

app = create_app()

@app.route('/finished', methods=['POST'])
def finished():
    task_url = None
    if request.form['msg'] == 'layout_not_completed':
        if request.form['role'] == 'user':
            painter_job_manager.add_row(request.form['task_id'])
        elif request.form['role'] == 'agent':
            instructor_job_manager.add_row(request.form['task_id'])
    else:
        print("layout completed: " + request.form['task_id'])

    response = jsonify(message="received")
    response.status_code = 200
    return response



# if __name__ == '__main__':
#     # app.run()
