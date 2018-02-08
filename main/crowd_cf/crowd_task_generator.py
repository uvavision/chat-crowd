import os
import re
import json
import csv
from .. import APP_DATA, APP_STATIC, get_crowd_db, get_chat_db
from ..core.utils import randomword
from ..core.const import *
from ..core.data import get_ts_str

DIALOG_DIR = os.path.join(APP_DATA, 'sample_dialog')
TEMPLATE_DIR = os.path.join(APP_DATA, 'templates')
CF_DIR = os.path.join(APP_DATA, 'cf')


def conversation_starter():
    in_csv = os.path.join(CF_DIR, 'conversation_starter.csv')
    csv_reader = csv.reader(open(in_csv, 'rb'))
    db_chat = get_chat_db()
    lst_content = []
    for i, row in enumerate(csv_reader):
        turn, role, text = row
        # task_id = randomword() + '-' + str(i)
        task_id = 'dialog-' + str(i)
        print(task_id)
        lst_content.append((turn, role, text))
        for turn, role, text in lst_content:
            r = {ROLE: role, TS: get_ts_str(), MSG: text, TASK_ID: task_id, TURN: int(turn)}
            db_chat.insert(r)


def get_tasks_incomplete():
    db_chat = get_chat_db()
    lst_task_completed = db_chat.distinct(TASK_ID, {MSG: "#END"})
    lst_task = db_chat.distinct(TASK_ID)
    lst_task_role = []
    for task_id in set(lst_task).difference(set(lst_task_completed)):
        role = db_chat.find({TASK_ID: task_id}).limit(1).sort("$natural", -1)[ROLE]
        role_to_be = [ele for ele in ['agent', 'user'] if ele != role][0]
        lst_task_role.append({TASK_ID: task_id, ROLE: role_to_be})
    return lst_task_role


def dialog_to_html(in_fn, out_fn):
    content_out = '<div>' # '<ul class="collection with-header">'
    if 'good' in in_fn:
        content_out += '<div class="collection-header"><b>A <span class="blue-text">Good</span> Example</b></div>'
    elif 'bad' in in_fn:
        content_out += '<div class="collection-header"><b>A <span class="red-text">Bad</span> Example</b></div>'
    for i, line in enumerate(open(in_fn, 'rb').xreadlines()):
        print(line)
        author, rest = line.strip().split(':', 1)
        if '\t' in rest:
            utterance, comment = rest.strip().rsplit('\t', 1)
            if 'good' in in_fn:
                c_comment = '<span class="blue-text">{}</span>'.format(comment)
            elif 'bad' in in_fn:
                c_comment = '<span class="red-text">{}</span>'.format(comment)
        else:
            utterance = rest.strip()
            c_comment = ''
        if author == 'YOU':
            c_author = '<b class="blue-text">{0}</b>'.format(author)
        else:
            c_author = '<b>{0}</b>'.format(author)
        content = '<div class="collection-item">{}: {} {}</div>\n'.format(c_author, utterance, c_comment)
        content_out += content
    content_out += '</div>' # '</ul>'
    open(out_fn, 'wb').write(content_out)


def combine_section_html(role, fn_in, out_head, output_dir=''):
    content = open(fn_in, 'rb').read()
    pattern = ur"\{\{(.+?)\}\}"
    lst_placeholder = []
    for m in re.finditer(pattern, content):
        place_holder = content[m.start(0):m.end(0)]
        print(place_holder)
        lst_placeholder.append(place_holder)
    for place_holder in lst_placeholder:
        html_fn = 'section_{}_{}.html'.format(place_holder[2:-2], role)
        content = content.replace(place_holder, open(os.path.join(TEMPLATE_DIR, html_fn)).read())
    fn_out = os.path.join(output_dir, '{}_{}.html'.format(out_head, role))
    print('##output_file', fn_out)
    open(fn_out, 'wb').write(content)


def combine_cml(role, in_cml, fn_html, fn_out):
    with open(fn_out, 'w') as outfile:
        for fn in [fn_html, in_cml]:
            with open(fn) as infile:
                for line in infile:
                    outfile.write(line)


def gen_html(role, dialog_dir=DIALOG_DIR, template_dir=TEMPLATE_DIR, output_dir=''):
    good_fn = os.path.join(dialog_dir, 'sample_dialog_good_{}.txt'.format(role))
    bad_fn = os.path.join(dialog_dir, 'sample_dialog_bad_{}.txt'.format(role))
    good_html = os.path.join(template_dir, 'section_example_good_{}.html'.format(role))
    bad_html = os.path.join(template_dir, 'section_example_bad_{}.html'.format(role))
    dialog_to_html(good_fn, good_html)
    dialog_to_html(bad_fn, bad_html)
    # in_layout_fn = template_dir + '/layout_section_tips_{}.html'.format(role)
    # out_head = 'section_tips'.format(role)
    # combine_section_html(role, in_layout_fn, out_head, template_dir)
    combine_section_html(role, template_dir + '/layout.html', 'instruction', output_dir)
    combine_section_html(role, template_dir + '/layout.html', 'instruction', template_dir)
    in_html = os.path.join(template_dir, 'instruction_{}.html'.format(role))
    out_cml = os.path.join(template_dir, 'instruction_{}.cml'.format(role))
    combine_cml(role, template_dir + '/confirmation.cml', in_html, out_cml)


if __name__ == '__main__':
    pass
    # conversation_starter()
    gen_html('mts', DIALOG_DIR, TEMPLATE_DIR, APP_STATIC)
    gen_html('agent', DIALOG_DIR, TEMPLATE_DIR, APP_STATIC)
    gen_html('user', DIALOG_DIR, TEMPLATE_DIR, APP_STATIC)
