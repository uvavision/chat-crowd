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
        sleep(1)
        if mode == MODE_BOT:
            if CONTEXT_ID in session:
                context_id = session[CONTEXT_ID]
            else:
                context_id = get_mts_cid()
                session[CONTEXT_ID] = context_id
            _, response = get_mts_response(context_id, msg)
            insert_chatdata(db_chat, session, {MSG: response, 'author': 'bot', ROLE: AGENT})
            emit('message', {MSG: get_message('agent', response), ROLE: 'agent', MODE: mode},
                 room=session.get(TASK_ID))


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
