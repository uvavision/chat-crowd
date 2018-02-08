import json
import os
from pprint import pprint
from .. import DOMAIN, VIZ_DATA_JSON
from ..core.mts_api import get_mts_metadata


def get_node(_id, name, group, weight, _type="", shape="ellipse"):
    d = {
      "data": {
        "id": str(_id),
        "idInt": _id,
        "name": name,
        "weight": weight,
        "query": True,
        "group": group,
        "type": _type,
        "faveShape": shape
      },
      "group": "nodes",
      "removed": False,
      "selected": False,
      "selectable": True,
      "locked": False,
      "grabbed": False,
      "grabbable": True
    }
    return d


def get_edge(target, source, _id, group, label=""):
    d = {"group": "edges", "locked": False, "selected": False, "classes": "",
         "grabbable": True, "selectable": True, "removed": False,
         "data": {"group": group, "target": str(target), "label": label,
         "weight": 0.43164432, "intn": True, "source": str(source),
         "id": 'e' + str(_id)}, "grabbed": False}
    # "networkId": 1229, "rIntnId": 569, "networkGroupId": 24
    return d


def gen_visual_data(out_fn=VIZ_DATA_JSON):
    res = get_mts_metadata()
    data_json = res
    lst = []
    _id = 0
    d_node = {}
    for k, v in data_json['data'].items():
        _id += 1
        d_node[k] = _id
        node = get_node(_id, k, 1, 180, "entity", "rectangle")
        lst.append(node)
        for k1, v1 in v.items():
            if type(v1) == list:
                if len(v1) > 100:
                    continue
                else:
                    for e in v1:
                        if e in d_node:
                            continue
                        _id += 1
                        d_node[e] = _id
                        node = get_node(_id, e, 2, 30, k1, "triangle")
                        lst.append(node)
            else:
                if v1 in d_node:
                    continue
                _id += 1
                d_node[v1] = _id
                node = get_node(_id, v1, 2, 30, k1, "triangle")
                lst.append(node)

    _eid = 0
    group = 0
    for k, v in data_json['data'].items():
        group += 1
        # if k != 'year_built': continue
        for k1, v1 in v.items():
            if type(v1) == list:
                if len(v1) > 100:
                    continue
                else:
                    for e in v1:
                        _eid += 1
                        edge = get_edge(d_node[e], d_node[k], _eid, group % 11,
                                        k1)
                        lst.append(edge)
            else:
                _eid += 1
                edge = get_edge(d_node[v1], d_node[k], _eid, group % 11, k1)
                lst.append(edge)

    json.dump(lst, open(out_fn, 'w'))
