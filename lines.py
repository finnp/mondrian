import numpy as np
import cv2
import myrustlib

def detect_lines_hough(img):
    lines = cv2.HoughLinesP(
        cv2.bitwise_not(opening),
        rho = 1,
        theta = np.pi / 2,
        threshold=50,
        minLineLength=120,
        maxLineGap=10
    )
    return [line[0] for line in lines] # weird HoughLinesP output

def detect_lines_rust(img, min_line_length):
    height, width = img.shape
    white = (img == 255).flatten().tolist()
    detected = myrustlib.detect_lines(white, width, height, min_line_length)
    return split_by_orientation(detected)

def detect_lines(img, min_line_length):
    """
        Custom line detection algorithm
    """
    height, width = img.shape
    horizontal = []
    vertical = []
    current_line = False
    current_line_start = 0

    white = img == 255

    for y in range(height):
        for x in range(width):
            is_white = white.item(y,x)
            if(is_white):
                if not current_line:
                    current_line = True
                    current_line_start = x
            else:
                if current_line:
                    current_line = False
                    if x - current_line_start > min_line_length:
                        horizontal.append((current_line_start, y, x - 1, y))
        if current_line:
            current_line = False
            if x - current_line_start > min_line_length:
                horizontal.append((current_line_start, y, x - 1, y))

    current_line = False
    current_line_start = 0
    for x in range(width):
        for y in range(height):
            is_white = white.item(y,x)
            if(is_white):
                if not current_line:
                    current_line = True
                    current_line_start = y
            else:
                if current_line:
                    current_line = False
                    if y - current_line_start > min_line_length:
                        vertical.append((x, y - 1, x, current_line_start))
        if current_line:
            current_line = False
            if y - current_line_start > min_line_length:
                vertical.append((x, y - 1, x, current_line_start))
    return (horizontal, vertical)

def remove_lines_close_to_border(horizontal, vertical, width, height, min_distance):
    horizontal_result = []
    vertical_result = []
    for h in horizontal:
        y = h[1]
        if y > min_distance and height - y > min_distance:
            horizontal_result.append(h)
    for v in vertical:
        x = v[0]
        if x > min_distance and width - x > min_distance:
            vertical_result.append(v)
    return (horizontal_result, vertical_result)


def split_by_orientation(lines):
    horizontal = []
    vertical = []
    for x1,y1,x2,y2 in lines:
        if (abs(y1-y2) > abs(x1-x2)):
            vertical.append((x1,y1,x2,y2))
        else:
            horizontal.append((x1,y1,x2,y2))
    return (horizontal, vertical)

def reduce_lines_rust(input_horizontal, input_vertical, min_distance):
    return myrustlib.reduce_lines(input_horizontal, input_vertical, min_distance)

def range_intersect(x1, x2, x1_b, x2_b):
    """
    Do the ranges [x1:x2] and [x1_b,x2] intersect, given x1 <= x2 and x1_b <= x2_b
    """
    return x1 <= x2_b and x1_b <= x2

def reduce_lines(input_horizontal, input_vertical, min_distance):
    """
        Takes a list of vertical and horizontal lines,
        tries to reduce them to essential lines eliminating lines close to each
        other.
    """

    seen_vertical = set()
    seen_horizontal = set()
    output_vertical = []
    output_horizontal = []

    # vertical
    for index, (x1,y1,x2,y2) in enumerate(input_vertical):
        if index in seen_vertical:
            continue
        x_values = [x1]
        y_ranges = [(y2,y1)]
        for other_index, (x1_b,y1_b,x2_b,y2_b) in enumerate(input_vertical):
            if other_index in seen_vertical:
                continue

            shortest_distance = min(abs(x - x1_b) for x in x_values)
            if (shortest_distance < 4):
                x_values.append(x1_b)
                y_ranges.append((y2_b,y1_b))
                seen_vertical.add(other_index)

        for (ry2,ry1,indices) in separate_ranges(y_ranges):
            x = int(np.mean([x_values[index] for index in indices]))
            output_vertical.append((x,ry1,x,ry2))

    for index, (x1,y1,x2,y2) in enumerate(input_horizontal):
        if index in seen_horizontal:
            continue
        x_ranges = [(x1,x2)]
        y_values = [y1]
        for other_index, (x1_b,y1_b,x2_b,y2_b) in enumerate(input_horizontal):
            if other_index in seen_horizontal:
                continue
            shortest_distance = min(abs(y - y1_b) for y in y_values)
            if (shortest_distance < 4):
                x_ranges.append((x1_b,x2_b))
                y_values.append(y1_b)
                seen_horizontal.add(other_index)

        for (rx1,rx2,indices) in separate_ranges(x_ranges):
            y = int(np.mean([y_values[index] for index in indices]))
            output_horizontal.append((rx1,y,rx2,y))

    return (output_vertical, output_horizontal)


def separate_ranges(ranges):
    """
        Given a list of ranges with elements (start,end) and start <= end find a
        list of ranges that can be separated without any other line intersecting
        the gap.
    """
    separated = []
    e = 50
    for index,(start,end) in enumerate(ranges):
        intersected = [r for r in separated if range_intersect(start+e,end-e,r[0],r[1])]
        not_intersected = [r for r in separated if not range_intersect(start+e,end-e,r[0],r[1])]
        if (len(intersected) == 0):
            separated.append((start,end,[index]))
        else:
            new_start = min([r[0] for r in intersected + [(start,end)]])
            new_end = max(r[1] for r in intersected + [(start,end)])
            indices = list(np.concatenate([r[2] for r in intersected]))
            indices.append(index)
            separated = not_intersected + [(new_start,new_end,indices)]
    return separated


def connect_lines(horizontal_lines, vertical_lines):
    """
        Makes sure the ends of every line are touching another line

        Possible improvements:
            - Prefer crossing lines in the direction of the end
                - e.g. the right end of a horizontal should rather connect to a vertical to the closest_vertical_right
            - Make sure the "crossing line" is actually long enough to cross this line
    """
    horizontal = []
    vertical = []

    for x1,y1,x2,y2 in horizontal_lines:
        closest_vertical_left = 20000
        closest_vertical_right = 20000
        e = 10
        for v_x1,v_y1,v_x2,v_y2 in vertical_lines:
            if not (y1 > v_y2 - e and y1 < v_y1 + e):
                continue
            if abs(x1 - v_x1) < abs(closest_vertical_left):
                closest_vertical_left = x1 - v_x1
            if abs(x2 - v_x1) < abs(closest_vertical_right):
                closest_vertical_right = x2 - v_x1
        x1 = x1 - closest_vertical_left
        x2 = x2 - closest_vertical_right
        horizontal.append((x1,y1,x2,y2))

    for x1,y1,x2,y2 in vertical_lines:
        closest_horizontal_up = 20000
        closest_horizontal_down = 20000
        for h_x1,h_y1,h_x2,h_y2 in horizontal_lines:
            if not (x1 > v_x1 - e and x1 < h_x2 + e):
                continue
            if abs(y1 - h_y1) < abs(closest_horizontal_up):
                closest_horizontal_up = y1 - h_y1
            if abs(y2 - h_y1) < abs(closest_horizontal_down):
                closest_horizontal_down = y2 - h_y1
        y1 = y1 - closest_horizontal_up
        y2 = y2 - closest_horizontal_down
        vertical.append((x1,y1,x2,y2))

    return (horizontal, vertical)


def find_rectangles(top_left, bottom_left, top_right):
    top_right.sort(key=lambda pos: pos[0])
    bottom_left.sort(key=lambda pos: pos[1])
    rectangles = []
    for x,y in top_left:
        x2,_ = next((tr for tr in top_right if tr[1] == y and tr[0] > x),(-1,0))
        if (x2 == -1):
            print('Error could not find top-right for', (x,y))
            continue
        _,y2 = next((bl for bl in bottom_left if bl[0] == x and bl[1] > y), (0,-1))
        if (y2 == -1):
            print('Error could not find top-right for', (x,y))
            continue
        w = x2 - x
        h = y2 - y
        rectangles.append((x,y,w,h))
    return rectangles



def find_corners(horizontal, vertical):
    top_left = []
    top_right = []
    bottom_left = []
    bottom_right = []

    for x_1,y_h,x_2,_ in horizontal:
        for x_v,y_1,_,y_2 in vertical:
            crossing = (x_v, y_h)
            if (x_v >= x_1 and x_v <= x_2 and y_h <= y_1 and y_h >= y_2):
                if (x_1 == x_v):
                    # left
                    if (y_1 != y_h):
                        bottom_left.append(crossing)
                    if (y_2 < y_h and y_1 > y_h):
                        top_left.append(crossing)
                elif (x_2 == x_v):
                    # right
                    if (y_1 != y_h):
                        bottom_right.append(crossing)
                    if (y_2 != y_h):
                        top_right.append(crossing)
                else:
                    if y_1 != y_h:
                        top_left.append(crossing)
                        top_right.append(crossing)
                    if y_2 != y_h:
                        bottom_left.append(crossing)
                        bottom_right.append(crossing)

    return (top_left, bottom_left, bottom_right, top_right)
