import json
from tqdm import tqdm
import os
os.environ['domain'] = '2Dshape'
from main import coll_anno
import numpy as np
import random


def sample_layout():
    grid_size = 100
    num_shapes = random.choice(range(4, 10))
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

if __name__ == '__main__':
    for i in range(100):
        cocoid = 12345 + i
        coll_anno.insert({"cocoid": cocoid, "boxes": sample_layout()})





