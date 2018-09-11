import cv2, numpy as np
import sys
import imutils
import datetime
from lines import remove_lines_close_to_border, connect_lines, reduce_lines, reduce_lines_rust, detect_lines_rust, find_corners, find_rectangles
from draw import find_colors_for_rects, draw_rectangles, draw_lines, draw_points, draw_corners, clip_rectangles
from files import process_pipeline
import timings

retr_type = cv2.RETR_LIST
contour_algorithm = cv2.CHAIN_APPROX_SIMPLE

binary_threshold = 110
min_line_length = 65
min_distance = 70
black_rectangle_dilate = 35

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(11,11))

def draw_black_border(img):
    height, width = img.shape[:2]
    cv2.rectangle(img, (0,0), (width, height), (0, 0, 0))

def process_image(original):
    timings.start('full')
    timings.start('start')
    steps = []
    height, width, channels = original.shape

    blurred = cv2.blur(original,(5,5))

    b_t,g_t,r_t = cv2.split(blurred)

    max = cv2.max(cv2.max(b_t, g_t), r_t)

    min = cv2.min(cv2.min(b_t, g_t), r_t)

    deviation = max - min
    steps.append(('deviation', deviation))
    # _, deviation = cv2.threshold(max - min, 25, 255, cv2.THRESH_BINARY)

    steps.append(('max', max))

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast_fixed = clahe.apply(max)

    steps.append(('contrast', contrast_fixed))

    color_contrast = cv2.add(contrast_fixed, deviation)

    steps.append(('color-contrast', color_contrast))

    _, binary = cv2.threshold(color_contrast, binary_threshold, 255, cv2.THRESH_BINARY)
    steps.append(('binary', binary))

    max = binary

    opening = cv2.erode(max, kernel)

    # remove lines, only black rectangles remain
    dilated = cv2.dilate(max, cv2.getStructuringElement(cv2.MORPH_RECT,(black_rectangle_dilate,black_rectangle_dilate)))

    remove_mask = cv2.bitwise_not(dilated)

    opening = cv2.max(opening, remove_mask)

    with_lines = np.copy(original)

    steps.append(('opening', opening))

    timings.end('start')
    timings.start('detect_lines')
    (horizontal, vertical) = detect_lines_rust(cv2.bitwise_not(opening), min_line_length)
    timings.end('detect_lines')
    timings.start('after')

    (vertical_lines, horizontal_lines) = reduce_lines_rust(horizontal, vertical, min_distance)
    (horizontal_lines, vertical_lines) = remove_lines_close_to_border(horizontal_lines, vertical_lines, width, height, 0.2 * min_distance)
    before_connect = np.copy(original)
    draw_lines(before_connect, horizontal, color=(0,255,0))
    draw_lines(before_connect, vertical, color=(255,0,0))
    draw_lines(before_connect, vertical_lines + horizontal_lines)
    steps.append(('raw-lines', before_connect))


    # add helper lines for borders
    horizontal_lines += [(0,0,width,0), (0,height,width,height)]
    vertical_lines += [(width,height,width,0), (0,height,0,0)]
    (horizontal, vertical) = connect_lines(horizontal_lines, vertical_lines)

    top_left, bottom_left, bottom_right, top_right = find_corners(horizontal, vertical)
    # add given image corners (should be done by find_corners)
    top_left.append((0,0))
    bottom_left.append((0,height))
    bottom_right.append((width,height))
    top_right.append((width,0))
    rectangles = find_rectangles(top_left, bottom_left, bottom_right, top_right)
    draw_corners(with_lines, top_left, (0, 90))
    draw_corners(with_lines, top_right, (90, 180))
    draw_corners(with_lines, bottom_right, (180, 270))
    draw_corners(with_lines, bottom_left, (270, 360))

    draw_lines(with_lines, horizontal + vertical)
    steps.append(('lines', with_lines))


    draw_black_border(opening)

    rects_with_color = find_colors_for_rects(rectangles, original)
    output = {
        'height': height,
        'width': width,
        'rectangles': rects_with_color,
        'options': {
            'binary_threshold': binary_threshold,
            'min_line_length': min_line_length,
            'min_distance': min_distance,
            'black_rectangle_dilate': black_rectangle_dilate
        }
    }
    drawn = draw_rectangles(rects_with_color, height, width)

    steps.append(('drawn', drawn))

    overlay = cv2.addWeighted(original, 0.3, drawn, 0.7,0)
    steps.append(('overlay', overlay))

    side_by_side = np.hstack((original, drawn, overlay))
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(side_by_side,str(len(rects_with_color)),(10,500), font, 4,(0,0,0),2,cv2.LINE_AA)
    steps.append(('side_by_side', side_by_side))


    timings.end('after')
    timings.end('full')
    return (steps, output)

process_pipeline(process_image)
print('')
print('Time for iteration: %s' % timings.average('full'))
print('Detect lines: %s' % timings.average('detect_lines'))
print('Before: %s' % timings.average('start'))
print('After lines: %s' % timings.average('after'))
