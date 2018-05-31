import json
import os
from flask import session
from flask_socketio import emit, join_room, leave_room
import datetime
from .. import socketio
from .. import get_crowd_db, get_chat_db, get_anno_db, add_bot_response
from .data import MSG, TURN
from .const import (ROLE, DEBUG, TASK_ID, USERNAME, AGENT, USER, MODE,
                    ROLE_NAME, canvas_token, DA)
from .data import (insert_crowd, insert_chatdata, get_chatdata, get_anno_data,
                   get_bot_response, insert_chatdata_cache)
from .interpreter import domain_entity_matcher, ner_matcher


def add_tag(text):
    doc, lst = domain_entity_matcher(text)
    # for ele in lst:
    #     print(str(ele))
    lst_out = [w.text for w in doc]
    for _, start, end in lst:
        lst_out[start] = '<span class="chip">' + lst_out[start]
        lst_out[end-1] = lst_out[end-1] + '</span>'
    _, lst_ner = ner_matcher(text)
    for _, start, end, label in lst_ner:
        lst_out[start] = '<span class="chip">' + lst_out[start]
        lst_out[end-1] = lst_out[end-1] + '</span>'
    return ' '.join(lst_out)


def get_message(role, text, username="ADMIN"):
    # if not text.startswith(canvas_token):
    #     text = add_tag(text)
    role_name = ROLE_NAME[role]
    if role == AGENT:
        return '<div><b>{0}({2}): </b>{1}</div>'.format(role_name, text, username)
    else:
        return "<b>{0}({2}): </b>{1}".format(role_name, text, username)


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
            emit('status', {MSG: get_message(ele[ROLE], "HIDDEN" + ele[MSG], ele[USERNAME]),
                            ROLE: ele[ROLE]}, room=session[TASK_ID])
        else:
            emit('status', {MSG: get_message(ele[ROLE], ele[MSG], ele[USERNAME]),
                            ROLE: ele[ROLE]}, room=session[TASK_ID])
    db_anno = get_anno_db(session[DEBUG])
    anno = get_anno_data(db_anno, session)
    if anno:
        boxes = anno['boxes'].replace("'", '"')
        boxes_data = json.loads(boxes)
        labels = list(set([anno['label'] for anno in boxes_data]))
        if os.environ['domain'] == '2Dshape':
            emit('2d_shape_anno', {"boxes": boxes}, room=session[TASK_ID])
        else: # COCO
            emit('coco_image_labels', {"labels": str(labels).replace("'", '"')}, room=session[TASK_ID])
            emit('coco_image_anno', {"url": anno['url'], "boxes": boxes}, room=session[TASK_ID])
    else:
        if os.environ['domain'] == '2Dshape':
            emit('2d_shape_anno', {}, room=session[TASK_ID])
        else:
            emit('coco_image_labels', {"labels": ""}, room=session[TASK_ID])
            emit('coco_image_anno', {}, room=session[TASK_ID])

    for ele in reversed(history):
        if ele['role'] == AGENT and ele['msg'].startswith(canvas_token):
            canvas_data = ele['msg'][len(canvas_token):]
            emit('latest_canvas', {MSG: str(canvas_data), ROLE: ele[ROLE]}, room=session[TASK_ID])
            break


@socketio.on('text', namespace='/chat')
def text(message):
    db_chat = get_chat_db(session[DEBUG])
    role = session.get(ROLE)
    mode = session.get(MODE)
    msg = message[MSG].strip()
    da = message[DA].strip()
    if msg:
        session[TURN] = session.get(TURN) + 1
        print(msg)
        insert_chatdata(db_chat, session, {MSG: msg, 'author': 'human', DA: da})
        # insert_chatdata_cache(session, {MSG: msg, 'author': 'human', DA: da})
        emit('message', {MSG: get_message(role, msg, session.get(USERNAME)),
             ROLE: role, MODE: mode}, room=session.get(TASK_ID))
        if role == AGENT:
            # if there are other painters in the same room, update their canvases too?
            if msg.startswith(canvas_token):
                emit('latest_canvas', {MSG: msg[len(canvas_token):], ROLE: role}, room=session[TASK_ID])
        if add_bot_response:
            other_role = {AGENT: USER, USER: AGENT}[role]
            response = get_bot_response(other_role)
            import time
            time.sleep(2)
            emit('message', {MSG: get_message(other_role, response),
                 ROLE: other_role, MODE: mode}, room=session.get(TASK_ID))


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
