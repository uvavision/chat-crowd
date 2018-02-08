from requests import Request, Session
from requests.utils import to_key_val_list
from pprint import pprint
from collections import defaultdict
from .const import LTE, GTE, DS
from .. import (COLL_NAME, MTS_API_URL, MTS_API_CID, MTS_API_CONTEXT,
                MTS_API_MESSAGE, MTS_API_KB)


class Connection(object):
    def __init__(self, cache=None, api_key=None, api_url=MTS_API_URL):
        self.api_key = api_key
        self.api_url = api_url
        self.context_id = None
        self._session = Session()

    def create_request(self, path, method='GET', **kw):
        url = self.api_url + path
        return Request(method=method, url=url, **kw)

    def send_request(self, req):
        '''
        returns requests.Response object
        raise
        '''
        # requests gotcha: even if send through the session, request.prepare()
        # does not get merged with the session's attributes, so we have to call
        # session.prepare_request(...)

        # merge params with the api key
        req.params = to_key_val_list(req.params)
        prepared_req = self._session.prepare_request(req)
        res = self._session.send(prepared_req)
        return res

    def set_context_id(self, context_id):
        self.context_id = context_id

    def request(self, path, method='GET', params=None, headers=None,
                data=None):
        # simple request helper
        if headers is None:
            headers = dict()
        headers.update(Accept='text/json')
        req = self.create_request(path, method=method, params=params,
                                  headers=headers, data=data)
        res = self.send_request(req)
        try:
            return res.json()
        except Exception as err:
            raise err
        return None


def context2dict(res_json):
    d_form = defaultdict(dict)
    if 'frame' in res_json:
        for k, v in res_json['frame'].items():
            for k1, v1 in v.items():
                if k1 == 'neg_values':
                    continue
                if k1 == 'operation':
                    op = v1[0]
                    if str(k) == 'price':
                        if op in ['<', '<=', '=']:
                            k = 'price_high'
                        if op in ['>', '>=']:
                            k = 'price_low'
                d_form[str(k)] = v1[0]
    return d_form


def dict2context(d_input):
    d_entity = {}
    d_context = {}
    for k, v in d_input.items():
        if v in ['', [], ['']]:
            continue
        if v in ['null', ['null']]:
            v = []
        elif type(v) != list:
            v = [v]
        if k in ['price_high', 'price_low']:
            operator = {'price_high': LTE, 'price_low': GTE}[k]
            if 'price' in d_context:
                d_context["price"]["pos_values"] += v
                d_context["price"]["operation"] += [operator]
            else:
                d_context["price"] = {'neg_values': [], "operation":
                                      [operator], 'pos_values': v}
        elif k == 'baths':
            if v == [0]:
                continue
            d_context[k] = {'neg_values': [], "operation": [GTE],
                            'pos_values': v}
        else:
            d_context[k] = {'neg_values': [], "operation": ['='], 'pos_values': v}
    return d_context


def get_mts_metadata():
        res = Connection().request(MTS_API_KB, method="GET")
        return res


def get_mts_cid():
    conn = Connection()
    res = conn.request(MTS_API_CID)
    context_id = str(res['conv_id'])
    conn.set_context_id(context_id)
    return context_id


def get_mts_response(context_id, user_utterance):
    data = [('conv_id', context_id), ('user_msg', user_utterance)]
    try:
        res = Connection().request(MTS_API_MESSAGE, method='PUT', data=data)
        ds = context2dict(res)
        return (ds, res['mts_utterance'])
    except Exception as err:
        return {}, 'ERROR', 'ERROR'


def post_mts_ds(context_id, d_in):
    ds = dict2context(d_in)
    if not ds:
        return None, None
    data = [('conv_id', context_id), ("frame", str(ds))]
    print("conv_id", context_id)
    try:
        res = Connection().request(MTS_API_CONTEXT, method='PUT',
                                   data=data)
    except Exception as err:
        print(err)
        return "ERROR", {}, "ERROR"
    return res['mts_utterance'], res['context']


if __name__ == '__main__':
    cid = get_mts_cid()
    print(cid)
    r = get_mts_response(cid, '2 beds in Bronx under $3000.')
    pprint(r)
    # get_mts_metadata()
