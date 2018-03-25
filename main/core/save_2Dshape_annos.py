import json
from tqdm import tqdm
import os
os.environ['domain'] = '2Dshape'
from main import coll_anno
import numpy as np
import random


def sample_2Dshape_random_layout():
    grid_size = 100
    num_shapes = random.choice(range(4, 6))
    positions = random.sample(range(25), num_shapes)
    layout = []
    for p in positions:
        row = p // 5
        col = p % 5
        top = col * grid_size + 10
        left = row * grid_size + 10
        width = grid_size - 20
        height = grid_size - 20
        label = random.choice(['red', 'green', 'blue'])
        shape = random.choice(['rectangle', 'circle', 'triangle'])
        layout.append({'left': left, 'top': top, 'width': width, 'height': height, 'label': label, 'shape': shape})
    return str(layout)

def make_entry(p, color, shape):
    grid_size = 100
    row = p // 5
    col = p % 5
    top = col * grid_size + 10
    left = row * grid_size + 10
    width = grid_size - 20
    height = grid_size - 20
    label = color
    return {'left': left, 'top': top, 'width': width, 'height': height, 'label': label, 'shape': shape}

def sample_2Dshape_pattern_layout():
    # pattern positions
    p2 = random.choice([6, 7, 8, 11, 12, 13, 16, 17, 18])
    k = random.random()
    if k < 0.25:
        p1 = p2 - 1
        p3 = p2 + 1
    elif k > 0.25 and k < 0.5:
        p1 = p2 - 5
        p3 = p2 + 5
    elif k > 0.5 and k < 0.75:
        p1 = p2 - 6
        p3 = p2 + 6
    else:
        p1 = p2 - 4
        p3 = p2 + 4
    assert p1 >= 0 and p1 < 25
    assert p2 >= 0 and p2 < 25
    assert p3 >= 0 and p3 < 25
   
    # pattern colors, shapes
    same_color = True
    same_shape = True
    k = random.random()
    if k > 0.5:
        same_color = False
    else:
        same_shape = False
    if same_color:
        c1 = c2 = c3 = random.choice(['red', 'green', 'blue'])
    else:
        c1 = random.choice(['red', 'green', 'blue'])
        c2 = random.choice(['red', 'green', 'blue'])
        c3 = random.choice(['red', 'green', 'blue'])

    if same_shape:
    	s1 = s2 = s3 = random.choice(['rectangle', 'circle', 'triangle'])
    else:
    	s1 = random.choice(['rectangle', 'circle', 'triangle'])
    	s2 = random.choice(['rectangle', 'circle', 'triangle'])
    	s3 = random.choice(['rectangle', 'circle', 'triangle'])

    layout = [make_entry(p1, c1, s1), make_entry(p2, c2, s2), make_entry(p3, c3, s3)]
    
    available_positions = list(set(range(25)) - set([p1, p2, p3]))
    
    num_shapes = random.choice(range(1, 3))
    other_positions = random.sample(available_positions, num_shapes)
    for p in other_positions:
        color = random.choice(['red', 'green', 'blue'])
        shape = random.choice(['rectangle', 'circle', 'triangle'])
        layout.append(make_entry(p, color, shape))
    return str(layout)

if __name__ == '__main__':
    for i in range(100):
        cocoid = 12345 + i
        coll_anno.insert({"cocoid": cocoid, "boxes": sample_2Dshape_random_layout()})
    for i in range(100):
        cocoid = 12345 + 100 + i
        coll_anno.insert({"cocoid": cocoid, "boxes": sample_2Dshape_pattern_layout()})
