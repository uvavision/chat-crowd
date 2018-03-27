import random
from collections import Counter
import os
import datetime

os.environ['domain'] = '2Dshape'
from main import coll_chat

actions = ['add', 'remove', 'move']

abs_loc_dict = {
    'top-left': (0, 0),
    'top-right': (0, 4),
    'bottom-left': (4, 0),
    'bottom-right': (4, 4),
    'center': (2, 2)
}

coord2abs_loc_name = {v: k for k, v in abs_loc_dict.items()}

relative_loc_dict = {
    'top-of': lambda row, col: (row - 1, col),
    'bottom-of': lambda row, col: (row + 1, col),
    'right-of': lambda row, col: (row, col + 1),
    'left-of': lambda row, col: (row, col - 1),
    'top-left-of': lambda row, col: (row - 1, col - 1),
    'top-right-of': lambda row, col: (row - 1, col + 1),
    'bottom-left-of': lambda row, col: (row + 1, col - 1),
    'bottom-right-of': lambda row, col: (row + 1, col - 1)
}

colors = ['red', 'green', 'blue']
shapes = ['square', 'circle', 'triangle']


class Object:
    def __init__(self, color, shape, row, col):
        self.color = color
        self.shape = shape
        self.row = row
        self.col = col
        self.identify_status = 'color-shape-location'

    def get_desc(self):
        assert self.identify_status in ['color-shape', 'location']
        if self.identify_status == 'color-shape':
            return "{} {}".format(self.color, self.shape)
        elif self.identify_status == 'location':
            return "{} {} on {} of the canvas".format(self.color, self.shape, coord2abs_loc_name[self.row, self.col])


class Canvas:
    def __init__(self):
        self.objects = []
        self.color_shape_cnt = Counter()

    def get_ref_obj(self):
        # randomly select an object identified by color-shape or abs location as reference
        available = [obj for obj in self.objects if
                     obj.identify_status == 'color-shape' or obj.identify_status == 'location']
        assert len(available) > 0
        return random.choice(available)

    def exec_instruction(self, inst):
        if isinstance(inst, AddInstruction):
            self.objects.append(inst.obj)
        elif isinstance(inst, RemoveInstruction):
            self.objects.remove(inst.target_obj)
        elif isinstance(inst, MoveInstruction):
            self.objects.remove(inst.remove_inst.target_obj)
            self.objects.append(inst.add_inst.obj)
        self.update_obj_identify_status()

    def update_obj_identify_status(self):
        self.color_shape_cnt = Counter(['{}-{}'.format(obj.color, obj.shape) for obj in self.objects])
        for obj in self.objects:
            if self.color_shape_cnt['{}-{}'.format(obj.color, obj.shape)] == 1:
                obj.identify_status = "color-shape"
            elif (obj.row, obj.col) in abs_loc_dict.values():
                obj.identify_status = "location"
            else:
                obj.identify_status = "color-shape-location"

    def get_desc(self):
        grid_size = 100
        layout = []
        for obj in self.objects:
            top = obj.row * grid_size + 10
            left = obj.col * grid_size + 10
            width = grid_size - 20
            height = grid_size - 20
            label = obj.color
            shape = obj.shape
            if shape == 'square':
                shape = 'rectangle'
            layout.append({"left": left, "top": top, "width": width, "height": height, "label": label, "shape": shape})
        return '#CANVAS-' + str(layout).replace("'", '"').replace(' ', '')


class Instruction:
    def __init__(self, ref_obj, relative_loc, abs_loc):
        # abs_loc: top-left ...
        # relative_loc: top-of ...
        if ref_obj:
            assert relative_loc
            assert not abs_loc
        if abs_loc:
            assert not ref_obj
            assert not relative_loc
        self.ref_obj = ref_obj
        self.relative_loc = relative_loc
        self.absolute_loc = abs_loc

    def viable(self, canvas):
        raise NotImplementedError

    def get_loc_desc(self):
        if self.absolute_loc:
            return self.absolute_loc + " of the canvas"
        if self.relative_loc:
            return "{} the {}".format(self.relative_loc, self.ref_obj.get_desc())


class AddInstruction(Instruction):
    def __init__(self, ref_obj, relative_loc, abs_loc, new_obj):
        super().__init__(ref_obj, relative_loc, abs_loc)
        self.obj = new_obj

    def viable(self, canvas):
        # the position to put the new object should be empty
        a = (self.obj.row, self.obj.col) not in [(obj.row, obj.col) for obj in canvas.objects]
        b = (0 <= self.obj.row <= 4 and 0 <= self.obj.col <= 4)
        return a and b

    def get_desc(self):
        # adding objects always requires specifying the location
        return "add a {} {} to {}".format(self.obj.color, self.obj.shape, self.get_loc_desc())


class RemoveInstruction(Instruction):
    def __init__(self, ref_obj, relative_loc, abs_loc, target_obj):
        super().__init__(ref_obj, relative_loc, abs_loc)
        assert target_obj
        self.target_obj = target_obj

    def viable(self, canvas):
        # the object to be removed must be on the canvas
        a = self.target_obj in canvas.objects
        b = (0 <= self.target_obj.row <= 4 and 0 <= self.target_obj.col <= 4)
        return a and b

    def get_desc(self):
        if self.target_obj.identify_status == 'color-shape':
            return "remove the {} {}".format(self.target_obj.color, self.target_obj.shape)
        else:
            return "remove the {} {} on {}".format(self.target_obj.color, self.target_obj.shape, self.get_loc_desc())


class MoveInstruction:
    def __init__(self, remove_inst, add_inst):
        # move instruction is a remove instruction following an add instruction
        # same color and shape, different position
        obj1 = remove_inst.target_obj
        obj2 = add_inst.obj
        assert (obj1.row, obj1.col) != (obj2.row, obj2.col) and \
               obj1.color == obj2.color and obj1.shape == obj2.shape
        self.remove_inst = remove_inst
        self.add_inst = add_inst

    def viable(self, canvas):
        return self.remove_inst.viable(canvas) and self.add_inst.viable(canvas)

    def get_desc(self):
        return "{} to {}".format(self.remove_inst.get_desc().replace("remove", "move"),
                                 self.add_inst.get_loc_desc())


def get_action_loc_abs(abs_loc):
    action_row, action_col = abs_loc_dict[abs_loc]
    return action_row, action_col


def get_action_loc_relative(ref_obj, relative_loc):
    action_row, action_col = relative_loc_dict[relative_loc](ref_obj.row, ref_obj.col)
    return action_row, action_col


def sample_abs_loc(canvas):
    abs_loc = random.choice(list(abs_loc_dict.keys()))
    action_row, action_col = get_action_loc_abs(abs_loc)
    return abs_loc, action_row, action_col


def sample_relative_loc(canvas):
    ref_obj = canvas.get_ref_obj()
    relative_loc = random.choice(list(relative_loc_dict.keys()))
    action_row, action_col = get_action_loc_relative(ref_obj, relative_loc)
    return ref_obj, relative_loc, action_row, action_col


def get_add_inst(canvas):
    while True:
        loc = 'abs' if len(canvas.objects) == 0 else random.choice(['abs', 'relative'])
        abs_loc = ref_obj = relative_loc = None
        if loc == 'abs':
            abs_loc, action_row, action_col = sample_abs_loc(canvas)
        if loc == 'relative':
            ref_obj, relative_loc, action_row, action_col = sample_relative_loc(canvas)

        new_obj = Object(random.choice(colors), random.choice(shapes), action_row, action_col)
        inst = AddInstruction(ref_obj, relative_loc, abs_loc, new_obj)
        if inst.viable(canvas):
            return inst


def get_remove_inst(canvas):
    assert len(canvas.objects) > 0
    while True:
        loc = 'abs' if len(canvas.objects) == 1 else random.choice(['abs', 'relative'])
        abs_loc = ref_obj = relative_loc = None
        if loc == 'abs':
            abs_loc, action_row, action_col = sample_abs_loc(canvas)
        if loc == 'relative':
            ref_obj, relative_loc, action_row, action_col = sample_relative_loc(canvas)
        target_obj = None
        for obj in canvas.objects:
            if (action_row, action_col) == (obj.row, obj.col):
                target_obj = obj
        # if target obj is not valid or target obj is the same with reference obj
        if not target_obj or (ref_obj and target_obj and ref_obj == target_obj):
            continue
        inst = RemoveInstruction(ref_obj, relative_loc, abs_loc, target_obj)
        if inst.viable(canvas):
            return inst


def get_move_inst(canvas):
    assert len(canvas.objects) > 0
    while True:
        remove_inst = get_remove_inst(canvas)
        add_inst = get_add_inst(canvas)
        # object to be removed cannot be used as reference
        while remove_inst.target_obj == add_inst.ref_obj:
            add_inst = get_add_inst(canvas)

        add_inst.obj.color = remove_inst.target_obj.color
        add_inst.obj.shape = remove_inst.target_obj.shape
        move_inst = MoveInstruction(remove_inst, add_inst)
        if move_inst.viable(canvas):
            return move_inst


def construct_next_instruction(canvas):
    weighted_actions = ['add'] * 5 + ['move'] * 3 + ['remove'] * 1
    action = 'add' if len(canvas.objects) == 0 else random.choice(weighted_actions)
    return {'add': get_add_inst, 'remove': get_remove_inst, 'move': get_move_inst}[action](canvas)


if __name__ == '__main__':
    canvas = Canvas()
    for i in range(50):
        inst = construct_next_instruction(canvas)
        print("{}: {}".format(i, inst.get_desc()))
        coll_chat.insert({'msg': inst.get_desc(), 'author': 'human', 'task_id': '12555',
                          'username': 'aaa', 'worker_id': '123456', "role": 'user', 'turn': str(i), 'mode': '2Dshape',
                          'timestamp': str(datetime.datetime.now())})
        canvas.exec_instruction(inst)
        coll_chat.insert({'msg': canvas.get_desc(), 'author': 'human', 'task_id': '12555',
                          'username': 'bbb', 'worker_id': '123456', "role": 'agent', 'turn': str(i), 'mode': '2Dshape',
                          'timestamp': str(datetime.datetime.now())})
