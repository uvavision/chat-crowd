import numpy as np
import pandas as pd
import collections
import itertools
import random
import datetime
from collections import Counter, defaultdict
import copy
import operator

from .const import (USERNAME, WORKER_ID, ROLE, TASK_ID, MSG, FEEDBACK, TURN,
                    TS, PRE_DEFINED_TASK, TEST, STRING, INTEGER, FLOAT, MODE,
                    USER, AGENT)
from .utils import randomword
from .metadata_processor import metadata_valuetype
from .. import APP_URL, coll_data, get_crowd_db, DOMAIN
UPPER_TIMES = 2

ptn = ['', '', '', '']
ptn[0] = 'I am looking for'
ptn[1] = 'Are there any'
ptn[2] = 'Can you help find'
ptn[3] = 'We need something like'

fmt = '%Y-%m-%d %H:%M:%S.%f'


def get_ts_str():
    # tzinfo = None
    return str(datetime.datetime.now())


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
    for r in db_chat.find({TASK_ID: task_id, MSG: {"$exists": 1}}).sort("$natural", 1):
        history.append({ROLE: r[ROLE], MSG: r[MSG], TURN: r[TURN]})
    return history


def get_coco_anno_data(db_coco_anno, session):
    task_id = session.get(TASK_ID)
    task_id = int(task_id)
    annos = []
    r = db_coco_anno.find({'cocoid': task_id}).sort("$natural", 1)
    assert r.count() == 1
    r0 = r[0]
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


def build_query(d_input):
    lst_single_value, lst_multiple_value = metadata_valuetype()
    OP_MAP = {'low': '$gte', 'high': '$lte'}
    d_query = {}
    for field, data_type in lst_single_value:
        if field not in d_input or not d_input[field]:
            continue
        val = d_input[field]
        if field.endswith('_low') or field.endswith('_high'):
            key, _range = field.rsplit('_', 1)
            d_query[key] = {OP_MAP[_range]: val}
    for field, data_type in lst_multiple_value:
        if field not in d_input or not d_input[field]:
            continue
        lst_v = d_input[field]
        lst_v = lst_v if type(lst_v) == list else [lst_v]
        if len(lst_v) == 0:
            continue
        if data_type in [STRING]:
            d_query[field] = {'$in': lst_v}
        elif data_type in [INTEGER]:
            if 0 in lst_v:
                lst_v += [np.nan, 0.5]  # bed - 5, 6
            d_query[field] = {'$in': lst_v}
        elif data_type in [FLOAT]:
            d_query[field] = {"$gte": d_input[field]}
    return d_query


def is_pass_test(db_crowd, worker_id, role):
    if worker_id in ['test123']:
        return True
    for r in db_crowd.find({WORKER_ID: worker_id, ROLE: role}):
        if r[TEST]:
            return True
    return False


def info_group(d_query, domain=None):
    if domain and domain == 'restaurants':
        info_group_res(d_query)
    else:
        info_group_apt(d_query)


def info_group_res(d_query):
    pass


def info_group_apt(d_query):
    d_lst = defaultdict(list)
    fields = ['price', 'beds', 'neighborhood', 'year_built']
    for r in coll_data.find(d_query):
        for field in fields:
            if field in r and not pd.isnull(r[field]):
                d_lst[field].append(r[field])
    step_price = 500
    step_year = 20
    d_top = defaultdict(list)
    for v_end, count in Counter(n - n % step_price + step_price
                                for n in d_lst['price']).most_common(3):
        d_top['price range'].append(('${0}-${1}'.format(v_end - step_price,
                                                        v_end - 1), count))
    for v_end, count in Counter(n - n % step_year + step_year
                                for n in d_lst['year_built']).most_common(3):
        d_top['year built'].append(('{0}-{1}'.format(v_end - step_year,
                                                     v_end - 1), count))
    for beds, count in Counter(d_lst['beds']).most_common(3):
        if int(beds) == beds:
            beds_str = str(int(beds))
        else:
            beds_str = str(beds)
        d_top['beds'].append((beds_str + '-bed', count))
    for neighborhood, count in Counter(d_lst['neighborhood']).most_common(3):
        d_top['neighborhood'].append((neighborhood, count))
    d_grouped_info = dict((k, v) for k, v in d_top.items() if len(v) > 1)
    return d_grouped_info


def get_grouped_info(d_query, domain=DOMAIN):
    results = coll_data.find(d_query)
    if results.count() > 0:
        return info_group(d_query, domain), None
    else:
        return None, query_variation(d_query)


def generate_task_data(begin, end, domain):
    if domain and domain == u'restaurants':
        return generate_task_data_res(begin, end)
    else:
        return generate_task_data_apt(begin, end)


def generate_task_data_res(begin, end):
    paras = ['categories', 'stars', 'neighborhood']
    d_lst = defaultdict(list)
    d_rand = {}
    for r in coll_data.find():
        d_lst['neighborhood'].append(r['neighborhood'])
        d_lst['categories'] += r['categories']
    d_rand['stars'] = np.arange(3, 5, 0.5).tolist()
    d_rand['neighborhood'] = [k for k, v in
                              Counter(d_lst['neighborhood']).most_common(20)]
    d_rand['categories'] = [k for k, v in
                            Counter(d_lst['categories']).most_common(20)]
    for i in range(begin, end + 1):
        taskid = randomword(8) + '-' + str(i)
        out_row = [i, taskid]
        sample_size = random.randint(1, len(paras))
        selected_paras = set(random.sample(paras, sample_size))
        selected_paras.add('neighborhood')
        d_input = {}
        for para in selected_paras:
            d_input[para] = random.choice(d_rand[para])
        text = quiz_text_gen(d_input, ptn[i % 4])
        d_query = build_query(d_input)
        results = coll_data.find(d_query)
        rcount = results.count()
        out_row += [text, rcount, int(rcount / 20.0)]
        for ele in paras:
            if ele in d_input:
                out_row.append(d_input[ele])
            else:
                out_row.append('')
        for role in [AGENT, USER]:
            url_str = '{0}taskid={1}&role={2}'.\
                format(APP_URL, taskid, role)
            out_row.append(url_str)
        yield out_row, d_input


def generate_task_data_apt(begin, end):
    paras = ['price_high', 'neighborhood', 'beds']  # 'price_low',
    d_lst = defaultdict(list)
    d_rand = {}
    for r in coll_data.find():
        d_lst['neighborhood'].append(r['neighborhood'])
    d_rand['price_high'] = np.arange(2000, 6001, 500).tolist()
    d_rand['price_low'] = np.arange(1500, 5001, 500).tolist()
    d_rand['beds'] = np.arange(1, 4, 1).tolist()
    d_rand['neighborhood'] = [k for k, v in
                              Counter(d_lst['neighborhood']).most_common(20)]
    for i in range(begin, end + 1):
        taskid = randomword(8) + '-' + str(i)
        out_row = [i, taskid]
        sample_size = random.randint(1, len(paras))
        selected_paras = set(random.sample(paras, sample_size))
        selected_paras.add('neighborhood')
        d_input = {}
        for para in selected_paras:
            d_input[para] = random.choice(d_rand[para])
        if 'price_low' in selected_paras and 'price_high' in selected_paras:
            v_high = random.choice(d_rand['price_high'])
            d_input['price_high'] = v_high
            d_input['price_low'] = random.choice(np.arange(1500, v_high,
                                                           500).tolist())
        elif 'price_low' in selected_paras:
            d_input['price_low'] = random.choice(d_rand['price_low'])
        elif 'price_high' in selected_paras:
            d_input['price_high'] = random.choice(d_rand['price_high'])
        text = quiz_text_gen(d_input, ptn[i % 4])
        d_query = build_query(d_input)
        results = coll_data.find(d_query)
        rcount = results.count()
        out_row += [text, rcount, int(rcount / 20.0)]
        for ele in paras:
            if ele in d_input:
                out_row.append(d_input[ele])
            else:
                out_row.append('')
        for role in [AGENT, USER]:
            url_str = '{0}taskid={1}&role={2}'.\
                format(APP_URL, taskid, role)
            out_row.append(url_str)
        yield out_row, d_input


def quiz_text_gen(d_input, ptn):
    t_beds = ' an'
    t_baths, t_neighborhood, t_transport, t_price = '', '', '', ''
    for k, v in d_input.items():
        if k == 'beds':
            if v == 0:
                t_beds = ' a studio'
            else:
                t_beds = ' a {}-bed'.format(v)
        if k == 'baths':
            t_baths = ' with {} baths'.format(v)
        if k == 'neighborhood':
            t_neighborhood = ' in {}'.format(v)
        if k == 'transport':
            t_transport = ' close to {}'.format(v)
    if 'price_high' in d_input and 'price_low' in d_input:
        t_price = ' preferably between ${} and ${}'.format(
                   d_input['price_low'], d_input['price_high'])
    elif 'price_high' in d_input:
        t_price = ' under ${}'.format(d_input['price_high'])
    elif 'price_low' in d_input:
        t_price = ' above ${}'.format(d_input['price_low'])
    text = ptn + '{t_beds} apartment{t_baths}{t_neighborhood}{t_transport}\
                  {t_price}.'.format(t_beds=t_beds, t_baths=t_baths,
                                     t_neighborhood=t_neighborhood,
                                     t_transport=t_transport, t_price=t_price)
    return text


def query_variation(d_query):
    def is_constraint_satisfied(filters, mappings, d_filter_new):
        for ele in filters:
            if 'constraint' in mappings[ele]:
                ele_constraint, ele_operator = mappings[ele]['constraint']
                if not ele_operator(d_filter_new[ele], ele_constraint):
                    return False
        return True

    def dict2lst(d_query_new):
        d = {}
        for k, v in d_query_new.items():
            d[k] = v.values()[0]
        lst = []
        for k, v in d.items():
            if type(v) == list:
                v_str = ', '.join([str(ele) for ele in v])
            else:
                v_str = str(v)
            k_str = str(k)
            lst.append((k_str, v_str))
        return lst
    mappings = collections.OrderedDict()  # should use sorted dict
    # single value based criteria
    if 'price' in d_query:
        price_original = d_query['price'].values()[0]
        p_constraint = UPPER_TIMES * price_original
        mappings['price'] = {'val_original': price_original, 'step': 200,
                             'op': operator.add,
                             'constraint': (p_constraint, operator.le)}
    if 'baths' in d_query:
        baths_original = d_query['baths'].values()[0]
        baths_constraint = 1
        mappings['baths'] = {'val_original': baths_original, 'step': 0.5,
                             'op': operator.sub,
                             'constraint': (baths_constraint, operator.ge)}
    # list based criteria
    # if 'beds' in d_query:
    #     lst_beds_original = d_query['beds'].values()[0]
    #     mappings['beds'] = {'val_original': lst_beds_original}
    #     lst_beds_constraint = range(min(beds_ori) - 1, max(beds_ori) + 2)
    #     mappings['beds'] = {'val_original': beds_ori, 'step': 0.5,
    #                          'op': operator.sub,
    #                         'constraint': (operator.sequenceIncludes,
    #                                        lst_beds_constraint)}
    # if 'transport' in d_query:
    #     lst_transport_original = d_query['transport'].values()[0]
    #     mappings['transport'] = {'val_original': lst_transport_original}
    lst_out = []
    filter_combinition = []  # iteration of different filter combinition
    for i in range(1, len(mappings) + 1):
        subset = list(itertools.combinations(mappings.keys(), i))
        filter_combinition += subset
    for filters in filter_combinition:
        d_query_new = copy.deepcopy(d_query)
        filters_changed = set()  # count of steps of changes, filters in order
        count_steps = 0
        d_filter_new = {}  # the new value of all the filters
        for ele in filters:
            d_filter_new[ele] = mappings[ele]['val_original']
        while is_constraint_satisfied(filters, mappings, d_filter_new):
            for ele in filters:
                val_new = d_filter_new[ele]
                if 'op' in mappings[ele]:
                    val_new = mappings[ele]['op'](val_new,
                                                  mappings[ele]['step'])
                elif type(val_new) == list and len(val_new) > 0:
                    val_new = val_new[:-1]
                    if len(val_new) == 0:
                        val_new = None
                if val_new:
                    for k, v in d_query[ele].items():
                        d_query_new[ele][k] = val_new
                else:
                    d_query_new.pop(ele, None)
                filters_changed.add(ele)
                count_steps += 1
                if val_new:
                    d_filter_new[ele] = val_new
                else:
                    d_filter_new[ele] = 'any'
            rcount = coll_data.find(d_query_new).count()
            if rcount > 0:
                lst_out.append((dict2lst(d_query_new), rcount,
                                filters_changed))
                break
    return lst_out


def gen_entry_custom(r, domain=DOMAIN):
    if domain == 'rental-apartments':
        return gen_entry_apartments(r)
    if domain == 'restaurants':
        return gen_entry_restaurants(r)


def gen_entry_restaurants(r):
    text = '||| '
    d_entry = {}
    address_str = '{name}, {neighborhood}, {city} {postal_code}'.\
                  format(name=r['name'], neighborhood=r['neighborhood'],
                         city=r['city'], postal_code=r['postal_code'])
    d_entry['name'] = address_str
    d_entry['stars'] = 'Star {0}'.format(r['stars'])
    d_entry['categories'] = r['categories']
    return d_entry, text


def gen_entry_apartments(r):
    text = '||| '
    d_entry = {}
    area_str = '{0}, {1}'.format(r['neighborhood'], r['borough'])
    address_str = '{addr}, {apt_no} ({area_str})'.\
                  format(addr=r['address'], area_str=area_str,
                         apt_no=r['apartment_number'])
    d_entry['address'] = address_str
    d_entry['price'] = '${0}'.format(r['price'])
    d_entry['owner_name'] = 'N/A'
    if 'owner_name' in r and r['owner_name']:
        d_entry['owner_name'] = r['owner_name']
    if 'phone_number' in r and r['phone_number']:
        d_entry['phone_number'] = r['phone_number']
    bed_str = ''
    if not np.isnan(r['beds']) and r['beds']:
        num_beds = r['beds']
        if int(num_beds) == num_beds:
            num_beds = int(num_beds)
        bed_str = '{0} bed'.format(num_beds)
        text += '{} beds apartment'.format(num_beds)
    else:
        bed_str = 'studio'
        text += ' studio apartment'
    d_entry['beds'] = bed_str
    d_entry['baths'] = ''
    if not np.isnan(r['baths']) and r['baths']:
        num_baths = r['baths']
        if int(num_baths) == num_baths:
            num_baths = int(num_baths)
        d_entry['baths'] = '{0} baths'.format(num_baths)
        text += ' with {} baths,'.format(num_baths)
    # if not np.isnan(r['sq_ft']) and r['sq_ft']:
    #     d_entry['sq_ft'] = '{0} sqft'.format(r['sq_ft'])
    #     text += ' {0} sqft '.format(r['sq_ft'])
    # else:
    #     d_entry['sq_ft'] = '-- sqft'
    if not np.isnan(r['year_built']) and r['year_built']:
        d_entry['year_built'] = 'built in {0}'.format(r['year_built'])
        text += ' Year {0} '.format(r['year_built'])
    else:
        d_entry['year_built'] = 'Year N/A'
    d_entry['transport'] = 'n/a'
    text += 'on {} in {}'.format(r['address'], r['neighborhood'])
    if 'transport' in r and len(r['transport']) > 0:
        d_entry['transport'] = '/'.join(sorted(r['transport']))
        text += ' close to subway ' + d_entry['transport']
    text += '. The rent is {}.'.format(d_entry['price'])
    return d_entry, text
