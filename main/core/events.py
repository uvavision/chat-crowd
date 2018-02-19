from flask import session
from flask_socketio import emit, join_room, leave_room
from eventlet import sleep
import datetime
from .. import socketio
from .. import get_crowd_db, get_chat_db
from .data import MSG, TURN
from .const import (ROLE, DEBUG, TASK_ID, USERNAME, AGENT, USER, MODE, MODE_BOT,
                    CONTEXT_ID)
from .data import (insert_crowd, insert_chatdata, get_chatdata)
from .mts_api import get_mts_cid, get_mts_response
import time
import json
import os
from multiprocessing import Queue

# with open('')
# print(os.getcwd())
cocoidQueue = Queue()
room2cocoid = dict()
with open('main/data/instances_tinycoco_all_2014_pretty.json', 'r') as f:
    tinycoco = json.load(f)
    cocoid2cocourl = {entry['id']: entry['coco_url'] for entry in tinycoco['images']}
    labelid2labelname = {category['id']: category['name'] for category in tinycoco['categories']}
    cocoid2boxanno = {}
    for anno in tinycoco['annotations']:
        cocoid = anno['image_id']
        box = anno['bbox']
        if cocoid not in cocoid2boxanno:
            cocoid2boxanno[cocoid] = []
        cocoid2boxanno[cocoid].append({"left": box[0], "top": box[1], "width": box[2], "height": box[3],
                                       "label": labelid2labelname[anno['category_id']]})
    for key in cocoid2cocourl.keys():
        cocoidQueue.put(key)
    # print(cocoid2boxanno[list(cocoid2cocourl.keys())[0]])
    # print(cocoidQueue)


# tinycoco = json.loads()

canvas_token = '#CANVAS-'
def get_message(role, text):
    if role == AGENT:
        return '<div><b class="blue-text">{0}: </b>{1}</div>'.format(role, text)
    else:
        return "<b>{0}: </b>{1}".format(role, text)


@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print("@@@ Client disconnected", str(datetime.datetime.utcnow()))


@socketio.on('connect', namespace='/chat')
def on_connect():
    print("@@@ Client connected", str(datetime.datetime.utcnow()))


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    is_debug = session[DEBUG]
    db_crowd = get_crowd_db(is_debug)
    task_id = session.get(TASK_ID)
    role = session.get(ROLE)
    username = session.get(USERNAME)
    print('##join', role, username, task_id)
    insert_crowd(db_crowd, session)
    session[TURN] = 0
    result = join_room(task_id)
    db_chat = get_chat_db(session[DEBUG])
    history = get_chatdata(db_chat, session)
    if history:
        session[TURN] = history[-1][TURN]
    for ele in history:
        emit('status', {MSG: get_message(ele[ROLE], ele[MSG]),
                        ROLE: ele[ROLE]}, room=session[TASK_ID])

    room = session[TASK_ID]
    if room not in room2cocoid:
        room2cocoid[room] = cocoidQueue.get()
    print(room2cocoid)
    coco_url = cocoid2cocourl[room2cocoid[room]]
    boxanno = cocoid2boxanno[room2cocoid[room]]
    emit('coco_image_anno', {"coco_url": coco_url, "boxanno": boxanno}, room=session[TASK_ID])
    for ele in reversed(history):
        if ele['role'] == 'agent' and ele['msg'].startswith(canvas_token):
            canvas_data = ele['msg'][len(canvas_token):]
            emit('latest_canvas', {MSG: str(canvas_data), ROLE: ele[ROLE]}, room=session[TASK_ID])
            break

    '''
    is_other_logged, username_other = get_role_other(role_other, taskid,
                                                     is_debug)
    msg = '{} ({}) has joined!'.format(username, role)
    emit('status', {MSG: msg, ROLE: role},
         taskid=taskid, role=role, username=username, room=room)
    if is_other_logged:
        role_other = [ele for ele in ['agent', 'user'] if ele != role][0]
        msg = '{} ({}) has joined!'.format(username_other, role_other)
        emit('status', {MSG: msg, ROLE: role_other}, taskid=taskid,
             role=role_other, username=username_other, room=room)
    '''


@socketio.on('text', namespace='/chat')
def text(message):
    db_chat = get_chat_db(session[DEBUG])
    role = session.get(ROLE)
    mode = session.get(MODE)
    msg = message[MSG].strip()
    if msg:
        session[TURN] = session.get(TURN) + 1
        insert_chatdata(db_chat, session, {MSG: msg, 'author': 'human'})
        emit('message', {MSG: get_message(role, msg), ROLE: role, MODE: mode},
             room=session.get(TASK_ID))
        if role == 'agent':
            assert msg.startswith(canvas_token)
            emit('latest_canvas', {MSG: msg[len(canvas_token):], ROLE: role}, room=session[TASK_ID])
        # sleep(1)
        # if mode == MODE_BOT:
        #     if CONTEXT_ID in session:
        #         context_id = session[CONTEXT_ID]
        #     else:
        #         context_id = get_mts_cid()
        #         session[CONTEXT_ID] = context_id
        #     _, response = get_mts_response(context_id, msg)
        #     insert_chatdata(db_chat, session, {MSG: response, 'author': 'bot', ROLE: AGENT})
        #     emit('message', {MSG: get_message('agent', response), ROLE: 'agent', MODE: mode},
        #          room=session.get(TASK_ID))



@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    db_chat = get_chat_db(session[DEBUG])
    task_id = session.get(TASK_ID)
    role = session.get(ROLE)
    leave_room(task_id)
    insert_chatdata(db_chat, session, {MSG: '#END'})
    emit('status', {MSG: role + ' has left the conversation.'}, room=task_id)
