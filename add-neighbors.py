import json, os
from itertools import combinations

dir = 'detected'
files = os.listdir(dir)

def do_overlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0])) > 0

def are_neighbours(a, b):
    a_x_interval = (a['x'], a['x'] + a['width'])
    b_x_interval = (b['x'], b['x'] + b['width'])
    horizontal_overlap = do_overlap(a_x_interval, b_x_interval)

    if horizontal_overlap:
        could_touch_up = a['y'] == b['y'] + b['height']
        could_touch_down = a['y'] + a['height'] == b['y']
        if could_touch_up or could_touch_down:
            return True

    a_y_interval = (a['y'], a['y'] + a['height'])
    b_y_interval = (b['y'], b['y'] + b['height'])
    vertical_overlap = do_overlap(a_y_interval, b_y_interval)

    if vertical_overlap:
        could_touch_right = a['x'] + a['width'] == b['x']
        could_touch_left = b['x'] + b['width'] == a['x']
        if could_touch_left or could_touch_right:
            return True

    return False

for file in files:
    with open(dir + '/' + file, 'r+') as f:
        data = json.load(f)
        rects = data['rectangles']
        for index, rect in enumerate(rects):
            rect['index'] = index
        edges = []
        for (rect_a, rect_b) in list(combinations(rects,2)):
            if are_neighbours(rect_a, rect_b):
                edges.append((rect_a['index'], rect_b['index']))
        data['edges'] = edges

        f.seek(0)
        f.write(json.dumps(data, indent=4))
        f.truncate()
