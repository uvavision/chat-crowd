from flask import session
from flask_socketio import emit, join_room, leave_room
from eventlet import sleep
import datetime
from .. import socketio
from .. import get_crowd_db, get_chat_db, get_coco_anno_db
from .data import MSG, TURN
from .const import (ROLE, DEBUG, TASK_ID, USERNAME, AGENT, USER, MODE, CONTEXT_ID)
from .data import (insert_crowd, insert_chatdata, get_chatdata, get_coco_anno_data)
import time
import json
import os
from multiprocessing import Queue
import requests

canvas_token = '#CANVAS-'
def get_message(role, text):
    role_name = {AGENT: 'painter', USER: 'instructor'}[role]
    if role == AGENT:
        return '<div><b>{0}: </b>{1}</div>'.format(role_name, text)
    else:
        return "<b>{0}: </b>{1}".format(role_name, text)


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
    canvas_indices = [i for i in range(len(history)) if history[i][MSG].startswith(canvas_token)]
    for i, ele in enumerate(history):
        # hide canvas if it's not the last one
        if len(canvas_indices) > 0 and i in canvas_indices[:-1]:
            emit('status', {MSG: get_message(ele[ROLE], "HIDDEN" + ele[MSG]),
                            ROLE: ele[ROLE]}, room=session[TASK_ID])
        else:
            emit('status', {MSG: get_message(ele[ROLE], ele[MSG]),
                            ROLE: ele[ROLE]}, room=session[TASK_ID])

    db_coco_anno = get_coco_anno_db(session[DEBUG])
    anno = get_coco_anno_data(db_coco_anno, session)
    if anno:
        boxes = anno['boxes'].replace("'", '"')
        boxes_data = json.loads(boxes)
        labels = list(set([anno['label'] for anno in boxes_data]))
        emit('coco_image_labels', {"labels": str(labels).replace("'", '"')}, room=session[TASK_ID])
        emit('coco_image_anno', {"url": anno['url'], "boxes": boxes}, room=session[TASK_ID])
    else:
        emit('coco_image_labels', {"labels": ""}, room=session[TASK_ID])
        emit('coco_image_anno', {}, room=session[TASK_ID])

    for ele in reversed(history):
        if ele['role'] == AGENT and ele['msg'].startswith(canvas_token):
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
        if role == AGENT:
            if msg.startswith(canvas_token):
                emit('latest_canvas', {MSG: msg[len(canvas_token):], ROLE: role}, room=session[TASK_ID])


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

@socketio.on('end_task', namespace='/chat')
def complete(message):
    task_id = session.get(TASK_ID)
    role = session.get(ROLE)
    r = requests.post("http://deep.cs.virginia.edu:5003/finished", data={'task_id': task_id, 'role': role, "msg": message[MSG]})
    # print(r.status_code, r.reason)


