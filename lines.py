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
        x = x1 as f64
        for other_index, (x1_b,y1_b,x2_b,y2_b) in enumerate(input_vertical):
            if other_index in seen_vertical:
                continue
            if (abs(x1 - x1_b) < min_distance):
                # if the end is further to the top, choose this end
                if (y2_b < y2):
                    y2 = y2_b
                # if the start if further to the bottom, choose it
                if (y1_b > y1):
                    y1 = y1_b

                x = (x_running_average + x1_b as f64) / 2.0
                seen_vertical.add(other_index)

            # taking the average x value for all the lines to get the middle
        x = int(np.mean(x_values))
        output_vertical.append((x,y1,x,y2))

    #horizontal
    for index, (x1,y1,x2,y2) in enumerate(input_horizontal):
        if index in seen_horizontal:
            continue
        y_values = [y1, y2]
        for other_index, (x1_b,y1_b,x2_b,y2_b) in enumerate(input_horizontal):
            if other_index in seen_horizontal:
                continue
            if (abs(y1 - y1_b) < min_distance):
                # if the start if further to the left, choose this point
                if (x1_b < x1):
                    x1 = x1_b
                # if the end is further to the right, choose it
                if (x2_b > x2):
                    x2 = x2_b

                y_values += [y1_b, y2_b]
                seen_horizontal.add(other_index)

            # taking the average y value for all the lines to get the middle
        y = int(np.mean(y_values))
        output_horizontal.append((x1,y,x2,y))

    return (output_vertical, output_horizontal)



def connect_lines(horizontal_lines, vertical_lines):
    """
        Makes sure the ends of every line are touching another line

        Possible improvements:
            - Prefer crossing lines in the direction of the end
                - e.g. the right end of a horizontal should rather connect to a vertical to the closest_vertical_right
            - Make sure the "crossing line" is actually long enough to cross this line

        Idea:
            - Test and improve this algorithm by
                - 1. create lines a la mondrian
                - 2. randomly shorten this lines
                - 3. run the algorithm over the sortened version
                - 4. check whether the result is the original
    """
    horizontal = []
    vertical = []

    for x1,y1,x2,y2 in horizontal_lines:
        closest_vertical_left = 20000
        closest_vertical_right = 20000
        for v_x1,v_y1,v_x2,v_y2 in vertical_lines:
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
            if abs(y1 - h_y1) < abs(closest_horizontal_up):
                closest_horizontal_up = y1 - h_y1
            if abs(y2 - h_y1) < abs(closest_horizontal_down):
                closest_horizontal_down = y2 - h_y1
        y1 = y1 - closest_horizontal_up
        y2 = y2 - closest_horizontal_down
        vertical.append((x1,y1,x2,y2))

    return (horizontal, vertical)


def find_rectangles(top_left, bottom_left, bottom_right, top_right):
    top_right.sort(key=lambda pos: pos[0])
    bottom_left.sort(key=lambda pos: pos[1])
    rectangles = []
    for x,y in top_left:
        a = [tr for tr in top_right if tr[1] == y and tr[0] > x]
        b = [bl for bl in bottom_left if bl[0] == x and bl[1] > y]
        if (len(a) == 0 or len(b) == 0):
            continue
        x2,_a = a[0]
        _,y2 = b[0]
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
                    if (y_2 != y_h):
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
