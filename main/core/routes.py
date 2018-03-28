import os
from flask import session, redirect, url_for, request, jsonify
from flask import render_template, render_template_string
from . import main
from .. import coll_data, APP_TEMPLATE, DOMAIN, CHAT_HTML
from .. import get_chat_db, get_crowd_db, get_anno_db
from .data import get_chatdata, get_anno_data
from .events import get_message
from .forms import (LoginForm, FeedbackForm, TestForm2DAgent, TestForm2DUser,
                    TestFormCOCOAgent, TestFormCOCOUser)
from .data import update_crowd, insert_chatdata, insert_crowd, is_pass_test
from .const import (ROLE, DEBUG, TASK_ID, USERNAME, CONTEXT_ID, WORKER_ID,
                    ROOM, PASS, MODE, TURN, MSG, TOTAL, ROLE_NAME,
                    USER, AGENT, MESSAGE, MODE_2D, MODE_COCO, TASKS, SEP)
from .utils import send_user_code, send_agent_code, get_confirmation_code, workerid_valid

from itertools import groupby


def _init_login_by_form(form):
    session.clear()
    session[WORKER_ID] = form.workerid.data
    session[USERNAME] = form.username.data
    # session[USERNAME] = "username_default"
    session[TASK_ID] = form.task_id.data
    if not form.tasks.data:
        session[TASKS] = [form.task_id.data]
    else:
        session[TASKS] = form.tasks.data
    session[TOTAL] = len(session[TASKS])
    session[ROLE] = form.role.data
    session[ROOM] = form.task_id.data
    session[MODE] = form.mode.data
    session[TURN] = 0


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    is_debug = True
    mode = session.get(MODE, MODE_2D)
    role = session.get(ROLE, AGENT)
    if form.validate_on_submit():
        _init_login_by_form(form)
        session[DEBUG] = is_debug
        session[PASS] = False  # if test mode available, set FALSE as default
        db_crowd = get_crowd_db(is_debug)
        workerid = session[WORKER_ID]
        role = session.get(ROLE, AGENT)
        mode = session.get(MODE, MODE_2D)
        if workerid and role:
            session[PASS] = is_pass_test(db_crowd, workerid, role)
        if session[PASS]:
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.test'))
    return render_template('index.html', form=form, mode=mode,
                           role=role, is_debug=is_debug)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if TASKS in request.args:
        tasks = request.args.get(TASKS).split(SEP)
        session[TASKS] = tasks
        task_id = tasks[0]
    else:
        task_id = request.args.get(TASK_ID)
        tasks = [task_id]
        session[TASKS] = [task_id]
    session[TOTAL] = len(tasks)
    room = task_id
    role = request.args.get(ROLE)
    is_debug = request.args.get('debug')
    mode = request.args.get(MODE)
    session[ROOM] = task_id
    session[TASK_ID] = task_id
    form.role.data = role
    form.task_id.data = task_id
    form.tasks.data = tasks
    form.mode.data = mode
    if form.validate_on_submit():
        _init_login_by_form(form)
        workerid = session[WORKER_ID]
        if not workerid_valid(workerid):
            form.workerid.errors = ['Your Contributor ID was not found...']
            return render_template('index.html', form=form, role=role,
                           mode=mode, room=room, is_debug=is_debug)
        session[PASS] = False  # if test mode available, set FALSE as default
        session[DEBUG] = bool(int(is_debug)) if is_debug else False
        session[MODE] = mode if mode else MODE_WOZ_HUMAN
        if workerid and role:
            db_crowd = get_crowd_db(is_debug)
            session[PASS] = is_pass_test(db_crowd, workerid, session[ROLE])
        if session[PASS]:
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.test'))
    return render_template('index.html', form=form, role=role,
                           mode=mode, room=room, is_debug=is_debug)


@main.route('/chat')
def chat():
    username = session.get(USERNAME, '')
    task_id = session.get(TASK_ID, '')
    if len(session[TASKS]) > 0:
        task_id = session[TASKS].pop()
    session[TASK_ID] = task_id
    role = session.get(ROLE, '')
    is_pass = session.get(PASS)
    mode = session.get(MODE)
    room = task_id
    if not is_pass:
        form = FeedbackForm()
        return render_template('end.html', room=room, form=form, code=None,
                               task_url_next=None)
    if username == '' or task_id == '':
        return redirect(url_for('.index'))
    db_chat = get_chat_db(session[DEBUG])
    role_name = ROLE_NAME[role]
    total = session[TOTAL]
    left = session[TOTAL] - len(session[TASKS])
    progress = 'task {} out of {}'.format(left, total)
    return render_template(CHAT_HTML, domain=DOMAIN, tasks=session[TASKS],
                           mode=mode, room=room, role_name=role_name,
                           role=role, username=username, progress=progress)


@main.route('/test', methods=['GET', 'POST'])
def test():
    task_id = session.get(TASK_ID)
    room = task_id
    role = session.get(ROLE)
    mode = session.get(MODE)
    username = session.get(USERNAME)
    is_pass = session.get(PASS)
    d_testform = {MODE_2D: {AGENT: TestForm2DAgent(), USER: TestForm2DUser()},
                  MODE_COCO: {AGENT: TestFormCOCOAgent(), USER: TestFormCOCOUser()}}
    form_test = d_testform[mode][role]
    if request.method == 'POST':
        answer_data = [form_test.r1.data, form_test.r2.data]
        print('@@ answer_data', answer_data, form_test.answers)
        if answer_data == form_test.answers:
            is_pass = True
        if is_pass:
            session[PASS] = is_pass
            is_debug = session[DEBUG]
            db_crowd = get_crowd_db(is_debug)
            session[TURN] = 0
            _id = None
            for r in db_crowd.find({TASK_ID: task_id}):
                _id = r['_id']
                break
            if not _id:
                _id = insert_crowd(db_crowd, session)
            else:
                update_crowd(db_crowd, _id, session)
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.end'))
    return render_template('test.html', mode='test', domain=DOMAIN,
                           form_test=form_test, role=role, room=room,
                           username=username)


@main.route('/end', methods=['GET', 'POST'])
def end():
    form = FeedbackForm()
    task_id = session.get(TASK_ID, '')
    is_pass = session.get(PASS)
    is_debug = session.get(DEBUG, '')
    workerid = session.get(WORKER_ID, '')
    task_url_agent_next = ""
    n_task = 1
    current_reward = 0
    estimated_reward = 0
    code = None
    if is_pass:
        code = get_confirmation_code(task_id)
        # role = session.get(ROLE)
        # if role == AGENT:
        #     status_code, reason = send_agent_code(session[WORKER_ID], code)
        # elif role == USER:
        #     status_code, reason = send_user_code(session[WORKER_ID], code)
        # else:
        #     assert False

    if request.method == 'POST':
        # form = FeedbackForm()
        feedback = form.feedback.data
        db_crowd = get_crowd_db(is_debug)
        session['feedback'] = feedback
        insert_crowd(db_crowd, session)
        return render_template('end.html', form=form, code=code,
                               n_task=n_task, message=MESSAGE,
                               current_reward=current_reward,
                               estimated_reward=estimated_reward,
                               task_url_next=task_url_agent_next)
    return render_template('end.html', form=form, code=code, n_task=n_task,
                           current_reward=current_reward,
                           estimated_reward=estimated_reward,
                           task_url_next=task_url_agent_next)

@main.route('/history', methods=['GET'])
def history():
    task_id = request.args.get(TASK_ID)
    print("requesting history of " + task_id)
    session = {'is_debug': False, 'task_id': task_id}

    db_anno = get_anno_db(session['is_debug'])
    anno = get_anno_data(db_anno, session)
    if anno:
        anno = '#CANVAS-' + anno['boxes'].replace("'", '"').replace(' ', '')
    else:
        anno = '#CANVAS-[]'

    db_chat = get_chat_db(session['is_debug'])
    history = get_chatdata(db_chat, session)
    groups = []
    uniquekeys = []
    for k, g in groupby(history, lambda x: x['username']+x['role']):
        groups.append(list(g))  # Store group iterator as a list
        uniquekeys.append(k)
    new_history = []
    for group in groups:
        msg = [g['msg'] for g in group]
        new_history.append({'role': group[0]['role'], 'username': group[0]['username'], 'msg': '\n'.join(msg)})

    anno = {'msg': anno}
    return render_template('history.html', task_id=task_id, anno=anno, history=history, role_mapping={'user': 'Instructor', 'agent': 'Painter'})
