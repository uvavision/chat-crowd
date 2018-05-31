import random
from collections import defaultdict
from vdial.utils import get_hashcode, xs
from string import Template
import re
from vdial.const import *


def tmpl2txt_act(act, da, role, t_obj, t_loc_abs="", t_loc_rel=""):
    if da == REQUEST and role == USER:
        tmpl = random.choice(DICT_TEMPLATES[act])
        s = Template(tmpl)
        text = s.substitute(obj=t_obj, loc_abs=t_loc_abs, loc_rel=t_loc_rel)
    return re.sub(' +', ' ', text)  # remove duplicated spaces


def tmpl2txt_da(role, da, act=None, d_para=None, is_viable=True):
    text = ''
    if da == REQUEST and role == USER:
        tmpl = random.choice(DICT_TEMPLATES[act])
        s = Template(tmpl)
        text = s.substitute(obj=d_para[T_OBJ], loc_abs=d_para[T_LOC_ABS], loc_rel=d_para[T_LOC_ABS])
    if da == REQUEST and role == AGENT:
        tmpl = random.choice(DICT_TEMPLATES[(da, role)])
        s = Template(tmpl)
        text = s.substitute(obj=d_para[OBJ], loc_abs=d_para[LOC_ABS], loc_rel=d_para[LOC_REL])
    if da == SELF_CORRECTION and role == USER:
        if len(d_para) == 1:
            tmpl = random.choice(DICT_TEMPLATES[(da, role, act, 0)])  #
            k, v = list(d_para.items())[0]
            s = Template(tmpl)
            text = s.substitute(k=k, v=v)
        elif len(d_para) == 2:
            tmpl = random.choice(DICT_TEMPLATES[(da, role, act, 1)])  #
            s = Template(tmpl)
            k1, k2 = d_para.keys()
            text = s.substitute(k1=k1, v1=d_para[k1], k2=k2, v2=d_para[k2])
    if da == ASK_Q and role == AGENT:
        if is_viable:
            tmpl = random.choice(DICT_TEMPLATES[(da, role)])
            s = Template(tmpl)
            text = s.substitute(obj=d_para[OBJ], loc_abs=d_para[T_LOC_ABS], loc_rel=d_para[T_LOC_REL])
        else:
            tmpl = random.choice(DICT_TEMPLATES[(da, role, act)])
            s = Template(tmpl)
            text = s.substitute(t_loc_abs=d_para[T_LOC_ABS], t_loc_rel=d_para[T_LOC_REL])
    if da in [CONFIRM, REJECT, END]:
        text = random.choice(DICT_TEMPLATES[(da, role)])
    text = re.sub(' +', ' ', text)
    return text


def get_rel_loc(obj1, obj2):
    row_d = obj1.row - obj2.row
    col_d = obj1.col - obj2.col
    if (row_d, col_d) in DICT_LOC_DELTA2NAME:
        return DICT_LOC_DELTA2NAME[(row_d, col_d)]
    return None


class Object:
    def __init__(self, color=None, shape=None, row=None, col=None):
        self.color = color
        self.shape = shape
        self.row = row
        self.col = col
        self.id_ = self.get_id()
        self.features = None
        self.loc_abs = None
        self.loc_rel = None
        self.obj_ref = None

    def __str__(self):
        return '{}; {}; row: {}; col: {}'.format(self.color,
                self.shape, self.row, self.col)

    def set(self, d_in):
        self.color = d_in[COLOR]
        self.shape = d_in[SHAPE]
        self.row = d_in[ROW]
        self.col = d_in[COL]
        self.id_ = self.get_id()
        self.loc_abs = d_in[LOC_ABS] if LOC_ABS in d_in else None
        self.loc_rel = d_in[LOC_REL] if LOC_REL in d_in else None
        self.obj_ref = d_in[OBJ_REF] if OBJ_REF in d_in else None

    def get_id(self):
        id_ = get_hashcode([self.color, self.shape, self.row, self.col])
        return id_

    def to_dict(self):
        d = {COLOR: self.color, SHAPE: self.shape, ROW: self.row, COL: self.col, ID: self.id_}
        return d


class Canvas:
    def __init__(self, grid_size=GRID_SIZE):
        self.d_id_obj = {}
        self.d_feature_id = defaultdict(list)  # key (color, shape)
        self.d_id_feature = defaultdict(list)
        self.d_id_rel = defaultdict(dict)
        self.d_grid_obj = {}  # currently not maintain all history
        self.grid_size = grid_size

    def size(self):
        return len(self.d_id_obj)

    def select_grid_obj_ref(self, select_empty=True, is_viable=True, excluded_grids=[]):
        if is_viable and self.size() - len(excluded_grids) <= 0:
            return None, None, None, None
        options = []
        for (row, col), obj_ref in self.d_grid_obj.items():
            if (row, col) in excluded_grids:
                continue
            for (row_d, col_d), loc_rel in DICT_LOC_DELTA2NAME.items():
                row_adj, col_adj = row + row_d, col + col_d
                if not (0 <= row_adj < self.grid_size and 0 <= col_adj < self.grid_size):
                    continue
                if select_empty and is_viable:
                    if (row_adj, col_adj) not in self.d_grid_obj:
                        options.append((row_adj, col_adj, obj_ref, loc_rel))
                elif not select_empty and is_viable:
                    if (row_adj, col_adj) in self.d_grid_obj:
                        options.append((row_adj, col_adj, obj_ref, loc_rel))
        if len(options) > 0:
            return random.choice(options)
        return None, None, None, None

    def select_grid_loc_abs(self, select_empty=True, excluded_grids=[]):
        l_all = list(DICT_LOC_ABS2NAME.keys())
        l_not_empty = [e for e in self.d_grid_obj.keys() if e]
        l_empty_abs = list(set(l_all) - set(l_not_empty))
        l_not_empty_abs = list(set(l_not_empty).intersection(set(l_all)))
        if select_empty:
            l_selected = l_empty_abs
        else:
            l_selected = l_not_empty_abs
        l_selected = list(set(l_selected) - set(excluded_grids))
        if l_selected is None or l_selected == []:
            return None, None, None
        row, col = random.choice(l_selected)
        return row, col, DICT_LOC_ABS2NAME[(row, col)]

    def get_obj_desc(self, obj,  mode_ref=None, mode_ref_loc=None, features=None):
        if not features:
            features = self.get_obj_features(obj, mode_ref)
        if len(features) > 0:
            random.shuffle(features)
            color, shape, loc_abs, loc_rel, obj_ref = None, None, None, None, None
            for color, shape, loc_abs, loc_rel, obj_ref in features:
                if loc_abs is None and loc_rel is None:
                    break
                if loc_abs and loc_rel is None:
                    break
            obj.features = {COLOR: obj.color, SHAPE: obj.shape,
                            LOC_ABS: loc_abs, LOC_REL: loc_rel,
                            OBJ_REF: obj_ref.to_dict() if obj_ref else None}
            tmpl = random.choice(DICT_TEMPLATES[OBJ])
            s = Template(tmpl)
            text = s.substitute(color=xs(color), shape=xs(shape))
            text += ' ' + self.get_loc_desc(loc_abs, loc_rel, obj_ref, mode_ref_loc)
            return re.sub(' +', ' ', text)
        return self.get_obj_ref_desc(obj)

    def get_obj_ref_desc(self, obj, mode_ref=None):
        features = self.get_obj_features(obj, mode_ref)
        random.shuffle(features)
        for shape, color, loc_abs, loc_rel, obj_ref in features:
            if loc_abs is None and loc_rel is None:
                return self.get_obj_desc(obj, mode_ref, mode_ref, [(shape, color, None, None, None)])
            if loc_abs is not None: # abs
                return self.get_obj_desc(obj, mode_ref, mode_ref)
            # if obj_ref: # obj_ref.row and obj_ref.col) in DICT_LOC_ABS2NAME:
            #     return self.get_obj_desc(obj, mode_ref, mode_ref)
        tmpl = random.choice(DICT_TEMPLATES[OBJ_REF])
        s = Template(tmpl)
        for (row_ref, col_ref), loc_abs in DICT_LOC_ABS2NAME.items():
            row_d = obj.row - row_ref
            col_d = obj.col - col_ref
            if (row_d, col_d) in DICT_LOC_DELTA2NAME:
                loc_rel = DICT_LOC_DELTA2NAME[(row_d, col_d)]
                text = s.substitute(color=obj.color, shape=obj.shape, loc_rel=loc_rel, loc_abs=loc_abs)
                return text
        return ''

    def get_loc_desc(self, loc_abs, loc_rel, obj_ref, mode_ref=None):
        mode_loc = None
        if loc_abs:
            mode_loc = LOC_ABS
        elif loc_rel:
            mode_loc = LOC_REL
        if mode_loc is None:
            return ''
        tmpl = random.choice(DICT_TEMPLATES[mode_loc])
        s = Template(tmpl)
        text = ''
        if mode_loc == LOC_ABS:
            text = s.substitute(loc_abs=loc_abs)
        if mode_loc == LOC_REL and obj_ref:
            t_obj_ref = self.get_obj_ref_desc(obj_ref, mode_ref)
            text = s.substitute(loc_rel=loc_rel, obj_ref=t_obj_ref)
        return text

    def get_desc(self):
        grid_size = 100
        layout = []
        for id, obj in self.d_id_obj.items():
            top = obj.row * grid_size + 10
            left = obj.col * grid_size + 10
            width = grid_size - 20
            height = grid_size - 20
            label = obj.color
            shape = obj.shape
            layout.append({"left": left, "top": top, "width": width, "height": height, "label": label, "shape": shape})
        return '#CANVAS-' + str(layout).replace("'", '"').replace(' ', '')

    def update_spatial_ref_add(self, obj_new):
        for id_, obj in self.d_id_obj.items():
            rel = get_rel_loc(obj, obj_new)
            if rel:
                self.d_id_rel[obj.id_][obj_new.id_] = rel
            rel = get_rel_loc(obj_new, obj)
            if rel:
                self.d_id_rel[obj_new.id_][obj.id_] = rel

    def update_spatial_ref_delete(self, obj_delete):
        if obj_delete.id_ in self.d_id_rel:
            del self.d_id_rel[obj_delete.id_]
        l_del = [k for k, v in self.d_id_rel.items() if obj_delete.id_ in v]
        for ele in l_del:
            del self.d_id_rel[ele][obj_delete.id_]

    def update_ref_obj_features(self):  # after action completed
        for id_, obj in self.d_id_obj.items():
            features = self.get_obj_features(obj)
            self.d_id_feature[id_] = features

    def is_action_viable(self, obj, act):
        if not (0 <= obj.row < self.grid_size and 0 <= obj.col < self.grid_size):
            return False
        if act == ADD:
            if (obj.row, obj.col) in self.d_grid_obj and self.d_grid_obj[(obj.row, obj.col)] is not None:
                return False
            return True
        if act == DELETE:
            if obj.id_ in self.d_id_obj or (obj.row, obj.col) in self.d_grid_obj:
                return True
            return False
        return False

    def add(self, obj):
        if self.is_action_viable(obj, ADD):
            self.d_id_obj[obj.id_] = obj
            self.d_grid_obj[(obj.row, obj.col)] = obj  # STATE_OCCU
            self.d_feature_id[(obj.color, obj.shape)].append(obj.id_)
            self.d_feature_id[obj.color].append(obj.id_)
            self.d_feature_id[obj.shape].append(obj.id_)
            self.update_spatial_ref_add(obj)
            return STATUS_SUCCESSFUL
        else:
            return STATUS_FAILED

    def delete(self, obj):
        if self.is_action_viable(obj, DELETE):
            if obj.id_ in self.d_id_obj:
                del self.d_id_obj[obj.id_]
            if (obj.row, obj.col) in self.d_grid_obj:
                obj = self.d_grid_obj[(obj.row, obj.col)]
                if obj.id_ in self.d_id_obj:
                    del self.d_id_obj[obj.id_]
                del self.d_grid_obj[(obj.row, obj.col)]
            if obj.id_ in self.d_id_rel:
                del self.d_id_rel[obj.id_]
            self.d_feature_id[(obj.color, obj.shape)].remove(obj.id_)
            self.d_feature_id[obj.color].remove(obj.id_)
            self.d_feature_id[obj.shape].remove(obj.id_)
            self.update_spatial_ref_delete(obj)
            return STATUS_SUCCESSFUL
        return STATUS_FAILED

    def get_obj_features(self, obj, mode_ref=None):
        # feature: color, shape, loc_abs, loc_rel, obj_ref
        lst = []
        loc_abs = loc_rel = obj_ref = None
        if (obj.row, obj.col) in DICT_LOC_ABS2NAME:
            loc_abs = DICT_LOC_ABS2NAME[(obj.row, obj.col)]
            lst.append((None, None, loc_abs, None, None))
        if obj.id_ in self.d_id_rel and len(self.d_id_rel[obj.id_]) > 1:
            options = []
            for obj_ref_id, loc_rel in self.d_id_rel[obj.id_].items():
                if obj_ref_id and obj_ref_id in self.d_id_obj:
                    obj_ref = self.d_id_obj[obj_ref_id]
                    if (obj_ref.row, obj_ref.col) in DICT_LOC_ABS2NAME:
                        options.append((loc_rel, obj_ref))
                    elif obj_ref_id in self.d_id_feature:
                        features = self.d_id_feature[obj_ref_id]
                        for _, _, loc_abs_, loc_rel_, obj_ref_ in features:
                            if loc_abs is None and loc_rel is None:
                                options.append((loc_rel, obj_ref))
                                break
            if len(options) > 0:
                random.shuffle(options)
                loc_rel, obj_ref = options[0]
                lst.append((None, None, None, loc_rel, obj_ref))
            else:
                loc_rel, obj_ref = None, None
        else:
            for id_, obj_r in self.d_id_obj.items():
                rel = get_rel_loc(obj, obj_r)
                if rel:
                    loc_rel, obj_ref = rel, obj_r
                    break
                # rel = get_rel_loc(obj_r, obj)
                # if rel:
                #     loc_rel, obj_ref = rel, obj_r
                #     break
        if mode_ref == MODE_FULL:
            lst_full = []
            if loc_abs:
                lst_full.append((obj.color, obj.shape, loc_abs, None, None))
            if loc_rel and obj_ref:
                lst_full.append((obj.color, obj.shape, None, loc_rel, obj_ref))
            return lst_full
        if obj.color in self.d_feature_id and len(self.d_feature_id[obj.color]) == 1:
            lst.append((obj.color, None, None, None, None))
        if obj.shape in self.d_feature_id and len(self.d_feature_id[obj.shape]) == 1:
            lst.append((None, obj.shape, None, None, None))
        if (obj.color, obj.shape) in self.d_feature_id and len(self.d_feature_id[(obj.color, obj.shape)]) == 1:
            lst.append((obj.color, obj.shape, None, None, None))
        if self.size() == 1:
            lst.append((None, None, None, None, None))
        return lst