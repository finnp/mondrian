import numpy as np
import cv2

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

def detect_lines(img):
    """
        Custom line detection algorithm
    """
    height, width = img.shape
    horizontal = []
    vertical = []
    current_line = False
    current_line_start = 0

    for y in range(height):
        for x in range(width):
            if(img[y,x] == 255):
                if not current_line:
                    current_line = True
                    current_line_start = x
            else:
                if current_line:
                    current_line = False
                    if x - current_line_start > 100:
                        horizontal.append((current_line_start, y, x - 1, y))
        if current_line:
            current_line = False
            if x - current_line_start > 100:
                horizontal.append((current_line_start, y, x - 1, y))

    current_line = False
    current_line_start = 0
    for x in range(width):
        for y in range(height):
            if(img[y,x] == 255):
                if not current_line:
                    current_line = True
                    current_line_start = y
            else:
                if current_line:
                    current_line = False
                    if y - current_line_start > 100:
                        vertical.append((x, y - 1, x, current_line_start))
        if current_line:
            current_line = False
            if y - current_line_start > 100:
                vertical.append((x, y - 1, x, current_line_start))
    return (horizontal, vertical)


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
        x_values = [x1,x2]
        for other_index, (x1_b,y1_b,x2_b,y2_b) in enumerate(input_vertical):
            if (abs(x1 - x1_b) < min_distance):
                # if the end is further to the top, choose this end
                if (y2_b < y2):
                    y2 = y2_b
                # if the start if further to the bottom, choose it
                if (y1_b > y1):
                    y1 = y1_b

                x_values += [x1_b, x2_b]
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
    lines = []

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
        lines.append((x1,y1,x2,y2))

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
        lines.append((x1,y1,x2,y2))

    return lines
