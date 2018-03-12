import os
from flask import session, redirect, url_for, request, jsonify
from flask import render_template, render_template_string
from . import main
from .. import coll_data, APP_TEMPLATE, DOMAIN, CHAT_HTML
from .. import get_chat_db, get_crowd_db
from .forms import (LoginForm, FeedbackForm, TestFormAgent, TestFormUser)
from .data import update_crowd, insert_chatdata, insert_crowd, is_pass_test
from .const import (ROLE, DEBUG, TASK_ID, USERNAME, CONTEXT_ID, WORKER_ID,
                    ROOM, PASS, MODE, TURN, MSG,
                    USER, AGENT, MESSAGE, MODE_2D, TASKS, SEP)


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
    session[ROLE] = form.role.data
    session[ROOM] = form.task_id.data
    session[MODE] = form.mode.data
    session[TURN] = 0


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    is_debug = True
    session[MODE] = MODE_2D
    if form.validate_on_submit():
        _init_login_by_form(form)
        session[DEBUG] = is_debug
        session[PASS] = False  # if test mode available, set FALSE as default
        db_crowd = get_crowd_db(is_debug)
        workerid = session[WORKER_ID]
        role = session[ROLE]
        # if workerid and role:
        #     session[PASS] = is_pass_test(db_crowd, workerid, role)
        session[PASS] = True
        if session[PASS]:
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.test'))
    return render_template('index.html', form=form, mode=session[MODE],
                           is_debug=is_debug)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    session[TASKS] = []
    if TASKS in request.args:
        tasks = request.args.get(TASKS).split(SEP)
        session[TASKS] = tasks
        task_id = tasks[0]
    else:
        task_id = request.args.get(TASK_ID)
        tasks = [task_id]
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
        session[PASS] = False  # if test mode available, set FALSE as default
        session[DEBUG] = bool(int(is_debug)) if is_debug else False
        session[MODE] = mode if mode else MODE_WOZ_HUMAN
        if workerid and role:
            db_crowd = get_crowd_db(is_debug)
            session[PASS] = is_pass_test(db_crowd, workerid, session[ROLE])
        session[PASS] = True
        if session[PASS]:
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.test'))
    return render_template('index.html', form=form, role=role,
                           mode=mode, room=room, is_debug=is_debug)


@main.route('/chat')
def chat():
    username = session.get(USERNAME, '')
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
    role_name = {AGENT: 'painter', USER: 'instructor'}[role]
    return render_template(CHAT_HTML, domain=DOMAIN, tasks=session[TASKS],
                           mode=mode, room=room, role_name=role_name,
                           role=role, username=username)


@main.route('/test', methods=['GET', 'POST'])
def test():
    task_id = session.get(TASK_ID)
    room = task_id
    role = session.get(ROLE)
    username = session.get(USERNAME)
    is_pass = session.get(PASS)
    if request.method == 'POST':
        if role == AGENT:
            form_test = TestFormAgent()
            answer_data = [form_test.r1.data, form_test.r2.data] # answers submitted
            # pass 90% of the test questions
            if sum([answer_data[i] == form_test.answers[i] for i in range(len(answer_data))]) >= 0.9 * len(answer_data):
                is_pass = True
            # compare answer_data with GOLD_ANSWERS
            # if pass threshold:
                # is_pass = True
        if role == USER:
            form_test = TestFormUser()
            answer_data = [form_test.r1.data, form_test.r2.data] # answers submitted
            # pass 90% of the test questions
            if sum([answer_data[i] == form_test.answers[i] for i in range(len(answer_data))]) >= 0.9 * len(answer_data):
                is_pass = True
            # compare answer_data with GOLD_ANSWERS
            # if pass threshold:
                # is_pass = True
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
    if role == USER:
        form_test = TestFormUser()
        return render_template('test.html', mode='test', domain=DOMAIN,
                               form_test=form_test, role=role, room=room, workerid=session[WORKER_ID],
                               username=session.get(USERNAME))
    if role == AGENT:
        form_test = TestFormAgent()
        # if 'rcount' in session and 'lst_q_data' in session:
        #     return render_template(TEST_HTML, form_test=form_test,
        #                            username=username, room=room,
        #                            role=role)
        return render_template('test.html', form_test=form_test,
                               mode='test', username=username, room=room,
                               role=role, domain=DOMAIN, workerid = session[WORKER_ID])
    return render_template('index.html')


@main.route('/end', methods=['GET', 'POST'])
def end():
    form = FeedbackForm()
    task_id = session.get(TASK_ID, '')
    is_pass = session.get(PASS)
    is_debug = session.get(DEBUG, '')
    task_url_agent_next = ""
    n_task = 1
    current_reward = 0
    estimated_reward = 0
    code = None
    if is_pass:
        code = str(int(task_id[::-1]) + 12345)
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
