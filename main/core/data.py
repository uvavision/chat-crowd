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
from pymongo import DESCENDING

from .const import (USERNAME, WORKER_ID, USER, AGENT, ROLE, TASK_ID, MSG,
                    FEEDBACK, TURN, MODE, TS, TEST, MODE_2D, MODE_COCO)
from .utils import randomword
from .. import TEST_DATA_FILE, coll_data, get_crowd_db, DOMAIN, get_chat_cache_db, get_chat_db, coll_cf_dispatch_semaphore


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


def insert_chatdata_cache(session, d_info):
    chatdata_cache_db = get_chat_cache_db()
    insert_chatdata(chatdata_cache_db, session, d_info)


def chatdata_flush(workerid, db_chat, username):
    # note race condition when multiple thread execute this function at the same time
    chatdata_cache_db = get_chat_cache_db()
    # db_chat.insert_many(chatdata_cache_db.find({WORKER_ID: workerid}).sort("timestamp", 1))
    to_save = []
    for r in chatdata_cache_db.find({WORKER_ID: workerid, USERNAME: username}).sort("timestamp", 1):
        last_entry = db_chat.find({TASK_ID: r[TASK_ID]}).sort("timestamp", DESCENDING).limit(1)
        if last_entry.count() == 0 or (last_entry[0][ROLE] != r[ROLE] and not last_entry[0]['msg'].startswith('#END')):
            to_save.append(r)
            # don't insert to db here in case there are multiple instructions
            # db_chat.insert(r)
    if len(to_save) > 0:
        db_chat.insert_many(to_save)
    updated_taskids = set([r[TASK_ID] for r in to_save])
    for taskid in updated_taskids:
        semaphore = get_dispatch_semaphore(taskid)
        if semaphore == 0:
            set_dispatch_semaphore(taskid, 1)
    chatdata_cache_db.delete_many({WORKER_ID: workerid, USERNAME: username})


def get_dispatch_semaphore(taskid):
    r = coll_cf_dispatch_semaphore.find({TASK_ID: taskid})
    assert r.count() == 1
    return r[0]['dispatch_semaphore']


def set_dispatch_semaphore(taskid, val):
    assert val in [0, 1]
    current_val = get_dispatch_semaphore(taskid)
    assert val != current_val
    coll_cf_dispatch_semaphore.update_one({TASK_ID: taskid}, {"$set": {'dispatch_semaphore': val}}, upsert=False)


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
