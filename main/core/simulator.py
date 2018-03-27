import json
from pprint import pprint


class Layout:

    def __init__(self):
        self.layout = {}

    def add(self, x, y, color, shape):
        pass

    def move(self, obj, x, y):
        pass

    def delete(self, x, y):
        pass

    def get_current_layout(self):
        return self.layout


def example():
    lst = []
    d = {}
    d['text-pattern'] = 'Draw a {color} {shape}'
    d['actions'] = ["add"] # add, move, delete, update
    d['object'] = {'name': 'obj1', 'color':'{color}', 'shape': '{shape}', 'x': 'x', 'y': 'y', 'mention': 'textual_reference'}
    lst.append(d)
    # pprint(d)

    d['text-pattern'] = 'Draw another {color} {shape} to the left of {object_reference of obj1}'
    d['actions'] = ["add"]
    d['object'] = {'name': 'obj2', 'color':'{color}', 'shape': '{shape}', 'x': 'x-1', 'y': 'y', 'mention': 'textual_reference'}
    lst.append(d)


    s = json.dumps(lst, indent=4, sort_keys=True)
    print(s)


def gen_object_reference(current_layout, context):
    pass


def instruction_validation(layout, instruction):
    '''
    '''
    return True


def gen_image_layout():
    pass

if __name__ == '__main__':
    example()
