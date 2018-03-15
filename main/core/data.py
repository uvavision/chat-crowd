import numpy as np
import pandas as pd
import collections
import itertools
import random
import datetime
from collections import Counter, defaultdict
import copy
import operator
import json
import os

from .const import (USERNAME, WORKER_ID, USER, AGENT, ROLE, TASK_ID, MSG,
                    FEEDBACK, TURN, MODE, TS, TEST, MODE_2D, MODE_COCO)
from .utils import randomword
from .. import APP_URL, TEST_DATA_FILE, coll_data, get_crowd_db, DOMAIN


fmt = '%Y-%m-%d %H:%M:%S.%f'


def get_ts_str():
    # tzinfo = None
    return str(datetime.datetime.now())


def get_bot_response(role=None):
    response = "Please proceed to next task or submit the job."
    # if role == AGENT:  # painter
    #     response = ""
    # if role == USER:  # instructor
    #     response = ""
    return response


def load_quiz_data(test_data_file=TEST_DATA_FILE):
    with open(test_data_file) as file_:
        return json.load(file_)


def get_role_other(role_other, task_id, is_debug):
    db_crowd = get_crowd_db(is_debug)
    ts_other, ts_curr = None, None
    username_other = None
    for r in db_crowd.find({TASK_ID: task_id}):
        if r[ROLE] == role_other:
            ts_other = datetime.datetime.strptime(str(r[TS]), fmt)
            username_other = r[USERNAME]
        else:
            ts_curr = datetime.datetime.strptime(str(r[TS]), fmt)
    if ts_other and ts_curr:
        delta = abs((ts_curr - ts_other).total_seconds())
        if delta < 60 * 10:
            return True, username_other
    return False, username_other


def get_task_count(role, worker_id, is_debug):
    db_crowd = get_crowd_db(is_debug)
    db_crowd.find({WORKER_ID: worker_id, ROLE: role}).count()


def insert_chatdata(db_chat, session, d_info):
    r = d_info
    for k in [TASK_ID, USERNAME, WORKER_ID, ROLE, TURN, MODE]:
        if k in session and k not in d_info:
            r[k] = session.get(k)
    r.update({TS: get_ts_str()})
    db_chat.insert(r)


def insert_crowd(db_chat, session):
    role = session.get(ROLE)
    r = {TASK_ID: session.get(TASK_ID), ROLE: role, TS: get_ts_str()}
    if FEEDBACK in session:
        r[FEEDBACK] = session.get(FEEDBACK)
    for k in [WORKER_ID, TEST, USERNAME]:
        r[k] = session.get(k)
    db_chat.insert(r)


def get_chatdata(db_chat, session):
    task_id = session.get(TASK_ID)
    history = []
    for r in db_chat.find({TASK_ID: task_id, MSG: {"$exists": 1}}).sort("timestamp", 1):
        history.append({ROLE: r[ROLE], MSG: r[MSG], TURN: r[TURN], USERNAME: r[USERNAME]})
    return history


def get_anno_data(db_anno, session):
    task_id = session.get(TASK_ID)
    try:
        task_id = int(task_id)
    except ValueError as e:
        return None
    annos = []
    r = db_anno.find({'cocoid': task_id})
    if r.count() == 0:
        return None
    assert r.count() == 1
    r0 = r[0]
    if os.environ['domain'] == '2Dshape':
        return {"boxes": r0["boxes"]}
    else: # COCO
        return {"url": r0['url'], "boxes": r0["boxes"], "captions": r0["captions"]}


def get_predefined_task(db_chat, session):
    task_id = session.get(TASK_ID)
    for r in db_chat.find({TASK_ID: task_id,
                           PRE_DEFINED_TASK: {"$exists": 1}}):
        return r[PRE_DEFINED_TASK]
    return None


def update_crowd(db_crowd, r_id, session):
    r = {TS: get_ts_str()}
    for k in [WORKER_ID, TEST]:
        r[k] = session.get(k)
    db_crowd.update({'_id': r_id}, {'$set': r})


def is_pass_test(db_crowd, worker_id, role):
    if worker_id in ['test123']:
        return True
    for r in db_crowd.find({WORKER_ID: worker_id, ROLE: role}):
        if r[TEST]:
            return True
    return False
