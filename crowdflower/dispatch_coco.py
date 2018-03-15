from flask import Flask
from flask import request
from flask import jsonify
import json
import requests

instructor_config = {
    "id": 1244174,
    "title": "instructor_job",
    'instruction_path': "../main/static/instructor-instruction/instructorinstruction.html",
    # "judgments_per_unit": 3,
    # "units_per_assignment": 5,
    # "pages_per_assignment": 1,
    # "max_judgments_per_worker": null,
    # "max_judgments_per_ip": null,
    # "gold_per_assignment": 0,
    # "minimum_account_age_seconds": null,
    # "execution_mode": "worker_ui_remix",
    # "payment_cents": 10,
    # "custom_key": null,
    # "design_verified": true,
    # "require_worker_login": null,
    # "public_data": false,
    # "variable_judgments_mode": "none",
    # "max_judgments_per_unit": null,
    # "expected_judgments_per_unit": null,
    # "min_unit_confidence": null,
    # "units_remain_finalized": null,
    # "auto_order_timeout": null,
    # "auto_order_threshold": null,
    # "completed_at": null,
    # "state": "unordered",
    # "auto_order": false,
    # "webhook_uri": null,
    # "send_judgments_webhook": null,
    # "language": "en",
    # "minimum_requirements": null,
    # "desired_requirements": null,
    # "order_approved": true,
    # "max_work_per_network": null,
    # "included_countries": [
    # ],
    # "excluded_countries": [
    # ],
    # "instructions": "",
    # "cml": null,
    # "js": null,
    # "css": null,
    # "problem": null,
    # "confidence_fields": null,
    # "gold": {
    # },
    # "units_count": 0,
    # "golds_count": 0,
    # "judgments_count": 0,
    # "support_email": "jdoe@crowdflower.com",
    # "crowd_costs": 0.0,
    # "completed": false,
    # "fields": null
}
painter_config = {
    "id": 1244173,
    "title": "painter_job",
    'instruction_path': "../main/static/painter-instruction/painterinstruction.html",
    # "judgments_per_unit": 3,
    # "units_per_assignment": 5,
    # "pages_per_assignment": 1,
    # "max_judgments_per_worker": null,
    # "max_judgments_per_ip": null,
    # "gold_per_assignment": 0,
    # "minimum_account_age_seconds": null,
    # "execution_mode": "worker_ui_remix",
    # "payment_cents": 10,
    # "custom_key": null,
    # "design_verified": true,
    # "require_worker_login": null,
    # "public_data": false,
    # "variable_judgments_mode": "none",
    # "max_judgments_per_unit": null,
    # "expected_judgments_per_unit": null,
    # "min_unit_confidence": null,
    # "units_remain_finalized": null,
    # "auto_order_timeout": null,
    # "auto_order_threshold": null,
    # "completed_at": null,
    # "state": "unordered",
    # "auto_order": false,
    # "webhook_uri": null,
    # "send_judgments_webhook": null,
    # "language": "en",
    # "minimum_requirements": null,
    # "desired_requirements": null,
    # "order_approved": true,
    # "max_work_per_network": null,
    # "included_countries": [
    # ],
    # "excluded_countries": [
    # ],
    # "instructions": "",
    # "cml": null,
    # "js": null,
    # "css": null,
    # "problem": null,
    # "confidence_fields": null,
    # "gold": {
    # },
    # "units_count": 0,
    # "golds_count": 0,
    # "judgments_count": 0,
    # "support_email": "jdoe@crowdflower.com",
    # "crowd_costs": 0.0,
    # "completed": false,
    # "fields": null
}

class JobManager:
    def __init__(self, role):
        self.api_key = 'guEi5sp-kQsXArgiESzj'
        self.role = role
        assert self.role in ['instructor', 'painter']
        self.config = {'instructor': instructor_config, 'painter': painter_config}[self.role]
        self.job_id = self.config['id']

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
        with open(self.config['instruction_path'], 'r') as f:
            instruction = f.read()
            url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
            data = {'job[instructions]': instruction}
            r = requests.put(url, data=data)
            r.raise_for_status()

    def set_job_cml(self):
        url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
        cml = """<div class="html-element-wrapper">
        <a class="clicked validates-clicked" href="{{taskurl}}" target="_blank">Click Here to go to the task</a>
        </div>
        <cml:text label="Confirmation Code" data-validates-regex="{{confirmation_code}}" 
        validates="required ss-required regex" data-validates-regex-message="Please copy and paste the code here that can be found at the end of the Survey" 
        default="Enter here..." 
        instructions="Enter Survey code in this field after completing"></cml:text>
        """
        data = {'job[cml]': cml}
        r = requests.put(url, data=data)
        r.raise_for_status()

    def set_judgements_per_rows(self):
        url = "https://api.crowdflower.com/v1/jobs/{}.json?key={}".format(self.job_id, self.api_key)
        data = {'job[max_judgments_per_unit]': '1'}
        r = requests.put(url, data=data)
        r.raise_for_status()


    def add_row(self, task_id):
        code = str(int(task_id[::-1]) + 12345)
        url = "https://api.crowdflower.com/v1/jobs/{}/units.json?key={}".format(self.job_id, self.api_key)
        role_mapping = {'instructor': 'user', 'painter': 'agent'}
        task_url = 'http://deep.cs.virginia.edu:8080/login?role={}&mode=chat&task_id={}'.format(role_mapping[self.role], task_id)
        data = {'unit[data][taskurl]': task_url, 'unit[data][confirmation_code]': code}
        r = requests.post(url, data=data)
        r.raise_for_status()

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


app = Flask(__name__)

instructor_job_manager = JobManager('instructor')
painter_job_manager = JobManager('painter')

instructor_job_manager.setup()
painter_job_manager.setup()
# task_ids = ['409707', '62652', '173814', '499141', '31090']
# task_ids = ['506740', '556500', '250380']
task_ids = ['506740', '556500', '250380', '287666', '319714', '547703']
# task_ids = ['549527', '47386', '420402', '29509', '278303', '520449']
for task_id in task_ids:
    instructor_job_manager.add_row(task_id)

# painter_job_manager.add_row('29509')

# TODO
# set Max Judgments per Contributor in Quality Control to 2


# instructor_job_manager.launch_job()
# painter_job_manager.launch_job()

#@app.route('/')
#def hello_world():
#    return 'Hello, World!'

@app.route('/finished', methods=['POST'])
def finished():
    task_url = None
    if request.form['role'] == 'user' and request.form['msg'] == 'layout_not_completed':
        painter_job_manager.add_row(request.form['task_id'])
        print("task {} send to painter".format(request.form['task_id']))
    elif request.form['role'] == 'agent':
        instructor_job_manager.add_row(request.form['task_id'])
        print("task {} send to instructor".format(request.form['task_id']))
    else:
        print("layout_completed: " + request.form['task_id'])

    response = jsonify(message="received")
    response.status_code = 200
    return response

# if __name__ == '__main__':
#     # app.run()
