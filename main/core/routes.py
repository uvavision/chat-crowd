import os
from flask import session, redirect, url_for, request, jsonify
from flask import render_template, render_template_string
from . import main
from .. import coll_data, APP_TEMPLATE, DOMAIN, CHAT_HTML
from .. import get_chat_db, get_crowd_db
from .forms import (LoginForm, LookupForm, TestFormAgent, TestFormUser,
                    FeedbackForm)
from .data import (build_query, get_grouped_info, gen_entry_custom,
                   is_pass_test, insert_crowd,
                   update_crowd, insert_chatdata, get_predefined_task)
from .data import generate_task_data
from .const import (ROLE, DEBUG, TASK_ID, USERNAME, CONTEXT_ID, WORKER_ID,
                    ROOM, PASS, MODE, MTS, DS, TURN, PRE_DEFINED_TASK, MSG,
                    INTEGER, STRING, FLOAT, USER, AGENT, MESSAGE, TOP_N,
                    MODE_WOZ_HUMAN, MODE_WOZ_MTS, MODE_BOT)
from .mts_api import (get_mts_cid, get_mts_response, post_mts_ds,
                      context2dict, dict2context)
from .metadata_processor import metadata_valuetype
from .. import SORTING_KEY, SORTING_ORDER, TEXT4DEBUG


def _init_login_by_form(form):
    session.clear()
    session[WORKER_ID] = form.workerid.data
    session[USERNAME] = form.username.data
    session[TASK_ID] = form.task_id.data
    session[ROLE] = form.role.data
    session[ROOM] = form.task_id.data
    session[MODE] = form.mode.data
    session[TURN] = 0


def lookupform_POST():
    d_in = {}
    lst_single_value, lst_multiple_value = metadata_valuetype()
    for label, data_type in lst_single_value:
        if data_type in [INTEGER, FLOAT]:
            MAP = {INTEGER: int, FLOAT: float}
            val = request.args.get(label, type=MAP[data_type])
            if val:
                d_in[label] = val
    for label, data_type in lst_multiple_value:
        if data_type in [STRING]:
            vals = request.args.get(label, type=str)
            if vals:
                d_in[label] = vals.split(',')
        elif data_type in [INTEGER]:
            d_in[label] = request.args.getlist(label + "[]", type=int)
        elif data_type in [FLOAT]:
            d_in[label] = request.args.get(label, 0, type=float)
    return d_in


@main.route('/woz/mts', methods=['GET', 'POST'])
def woz():
    form = LoginForm()
    session[ROLE] = AGENT
    if form.validate_on_submit():
        _init_login_by_form(form)
        workerid = session[WORKER_ID]
        session[PASS] = False
        session[DEBUG] = True
        session[MODE] = MODE_WOZ_MTS
        role = session[ROLE]
        if workerid and role:
            db_crowd = get_crowd_db(session[DEBUG])
            session[PASS] = is_pass_test(db_crowd, workerid, role)
        if session[PASS]:
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.test'))
    return render_template('index.html', form=form, role=session[ROLE],
                           is_debug=session[DEBUG], mode=session[MODE])


@main.route('/woz/mts/get')
def mts_get():
    db_chat = get_chat_db(session[DEBUG])
    for r in db_chat.find({ROLE: USER}).limit(1).sort("$natural", -1):
        if MSG in r:
            user_utterance = r[MSG]
    ds = {}
    mts_utterance = 'ERROR. '
    if CONTEXT_ID not in session or not session[CONTEXT_ID]:
        try:
            session[CONTEXT_ID] = get_mts_cid()
        except Exception as err:
            print(err)
    cid = session[CONTEXT_ID]
    query = ''
    try:
        # if session[DEBUG]:
        #     user_utterance = "I am looking for 4 bed apartments under $30000 in Tribeca."
        #     user_utterance = "I want to find restaurants in the Annex with 4 stars."
        ds, mts_utterance = get_mts_response(cid, user_utterance)
    except Exception as err:
        print(err)
    session[TURN] += 1
    insert_chatdata(db_chat, session,
                    {DS: ds, 'author': MTS, 'mts_utterance': mts_utterance})
    d_res = {"mts_utterance": mts_utterance, "usr_msg": user_utterance}
    if len(ds.items()) > 0:
        d_res.update(ds)
    return jsonify(d_res)


@main.route('/woz/mts/post')
def lookupform_post():
    d_input = lookupform_POST()
    mts_utterance = ''
    ds = {}
    try:
        if CONTEXT_ID not in session:
            context_id = get_mts_cid()
            session[CONTEXT_ID] = context_id
        mts_utterance, ds = post_mts_ds(session[CONTEXT_ID], d_input)
    except Exception as err:
        print(err)
        return jsonify({'mts_utterance': 'ERROR'})
    db_chat = get_chat_db(session[DEBUG])
    session[TURN] += 1
    insert_chatdata(db_chat, session, {DS: ds, 'author': 'human',
                                       'mts_utterance': mts_utterance})
    d_res = dict2context(ds)
    d_res['mts_utterance'] = mts_utterance
    return jsonify(d_res)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    is_debug = True
    session[MODE] = MODE_WOZ_HUMAN
    if form.validate_on_submit():
        _init_login_by_form(form)
        session[DEBUG] = is_debug
        session[PASS] = False
        db_crowd = get_crowd_db(is_debug)
        workerid = session[WORKER_ID]
        role = session[ROLE]
        if workerid and role:
            session[PASS] = is_pass_test(db_crowd, workerid, role)
        if session[PASS]:
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.test'))
    return render_template('index.html', form=form, mode=session[MODE],
                           is_debug=is_debug)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    task_id = request.args.get(TASK_ID)
    room = task_id
    role = request.args.get(ROLE)
    is_debug = request.args.get('debug')
    mode = request.args.get(MODE)
    session[ROOM] = task_id
    session[TASK_ID] = task_id
    form.role.data = role
    form.task_id.data = task_id
    if form.validate_on_submit():
        _init_login_by_form(form)
        workerid = session[WORKER_ID]
        session[PASS] = False
        session[DEBUG] = bool(int(is_debug)) if is_debug else False
        session[MODE] = mode if mode else MODE_WOZ_HUMAN
        if workerid and role:
            db_crowd = get_crowd_db(is_debug)
            session[PASS] = is_pass_test(db_crowd, workerid, session[ROLE])
        if session[PASS]:
            return redirect(url_for('.chat'))
        else:
            return redirect(url_for('.test'))
    return render_template('index.html', form=form, role=session[ROLE],
                           mode=mode, room=room, is_debug=is_debug)


@main.route('/_lookup', methods=['GET', 'POST'])
def lookup():
    d_in = lookupform_POST()
    db_chat = get_chat_db(session[DEBUG])
    insert_chatdata(db_chat, session, {DS: d_in})
    d_query = build_query(d_in)
    idx = 0
    entries = []
    for r in coll_data.find(d_query).sort(SORTING_KEY, SORTING_ORDER):
        d_entry = {}
        idx += 1
        d_entry, text = gen_entry_custom(r)
        d_entry['id'] = idx
        entries.append((d_entry, text))
    result_html = os.path.join(APP_TEMPLATE, DOMAIN + '.results.html')
    html_content_r = open(result_html, 'r').read()
    html_results = render_template_string(html_content_r,
                                          entries=entries[:TOP_N])
    html_more = ''
    n, n1 = 0, 0
    if entries and len(entries) > 0:
        n = len(entries)
        info_html = os.path.join(APP_TEMPLATE, 'info.html')
        html_content_i = open(info_html, 'r').read()
        d_group, lst_alter = get_grouped_info(d_query)
        html_more = render_template_string(html_content_i, d_group=d_group,
                                           lst_alter=lst_alter)
        if lst_alter:
            n1 = len(lst_alter)
        elif d_group:
            n1 = len(d_group)
    return jsonify(result=html_results, count=n, count1=n1, more=html_more)


@main.route('/chat')
def chat():
    """Chat session. The user's username and task_id must be stored in
    the session."""
    username = session.get(USERNAME, '')
    task_id = session.get(TASK_ID, '')
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
    form = LookupForm()
    db_chat = get_chat_db(session[DEBUG])
    filters = []
    if role == USER:
        d_pre_task = get_predefined_task(db_chat, session)
        if not d_pre_task:
            for ele in generate_task_data(1, 1, DOMAIN):
                task_data, d_pre_task = ele
                insert_chatdata(db_chat, session,
                                {PRE_DEFINED_TASK: d_pre_task})
        filters = sorted(d_pre_task.items())
    role_name = {AGENT: 'painter', USER: 'instructor'}[role]
    return render_template(CHAT_HTML, domain=DOMAIN, form=form,
                           mode=mode, room=room, role_name=role_name,
                           role=role, username=username, filters=filters)


@main.route('/test', methods=['GET', 'POST'])
def test():
    form = LookupForm()
    task_id = session.get(TASK_ID)
    room = task_id
    role = session.get(ROLE)
    username = session.get(USERNAME)
    is_pass = session.get(PASS)
    if request.method == 'POST':
        if role == AGENT:
            form_test = TestFormAgent()
            tests = [form_test.r1.data, form_test.r2.data, form_test.r3.data]
            count = len(list(set(tests) & set(session['rcount'])))
            print('@@@ test', tests, 'Answers:', session['rcount'])
            if count >= 2:
                is_pass = True
        if role == USER:
            form_test = TestFormUser()
            test1 = form_test.rental.data
            test2 = form_test.neighborhood.data
            answer1 = ['1', '2', '3', '4']
            answer2 = ['Downtown Brooklyn', 'Tribeca', 'Midtown']
            n1 = len(list(set(test1) & set(answer1)))
            n2 = len(list(set(test2) & set(answer2)))
            if n1 >= 3 and n2 >= 2:
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
    role_name = {AGENT: 'painter', USER: 'instructor'}[role]
    if role == USER:
        form_test = TestFormUser()
        return render_template(CHAT_HTML, form=form, mode='test', role_name=role_name,
                               form_test=form_test, role=role, room=room)
    if role == AGENT:
        form_test = TestFormAgent()
        if 'rcount' in session and 'lst_q_data' in session:
            return render_template(CHAT_HTML, form=form, form_test=form_test,
                                   username=username, room=room, role_name=role_name,
                                   role=role, lst_q_data=session['lst_q_data'])
        session['rcount'] = []
        room = session[TASK_ID]
        lst_q_data = []
        for data, _ in generate_task_data(1, 4):
            lst_q_data.append((data[2], data[3]))
            session['rcount'].append(data[3])
        session['lst_q_data'] = lst_q_data
        if session[DEBUG]:
            print('@@@ answers: ', session['rcount'])
        return render_template(CHAT_HTML, form=form, form_test=form_test,
                               mode='test', username=username, room=room,
                               role=role, lst_q_data=lst_q_data)
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
        code = task_id[::-1]
    if request.method == 'POST':
        form = FeedbackForm()
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


@main.route('/kbv', methods=['GET', 'POST'])
def kbv():
    return render_template('kbv.html', domain=DOMAIN)
