import cv2, numpy as np
import sys
import imutils
import datetime
from lines import remove_lines_close_to_border, connect_lines, reduce_lines, reduce_lines_rust, detect_lines_rust, detect_lines_hough, find_corners, find_rectangles
from draw import draw_circle, find_colors_for_rects, draw_rectangles, draw_lines, draw_points, draw_corners, clip_rectangles
from files import run_pipeline
import timings

retr_type = cv2.RETR_LIST
contour_algorithm = cv2.CHAIN_APPROX_SIMPLE

binary_threshold = 110
min_line_length = 40
min_distance = 70
black_rectangle_dilate = 40

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(11,11))

def preprocessing(original):
    steps = []
    height, width, channels = original.shape

    blurred = cv2.blur(original,(5,5))

    b_t,g_t,r_t = cv2.split(blurred)

    max = cv2.max(cv2.max(b_t, g_t), r_t)

    min = cv2.min(cv2.min(b_t, g_t), r_t)

    deviation = max - min
    steps.append(('deviation', deviation))

    steps.append(('max', max))

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast_fixed = clahe.apply(max)

    steps.append(('contrast', contrast_fixed))

    color_contrast = cv2.add(contrast_fixed, deviation)
    steps.append(('color-contrast', color_contrast))

    _, binary = cv2.threshold(color_contrast, binary_threshold, 255, cv2.THRESH_BINARY)
    steps.append(('binary', binary))

    # opening = cv2.erode(binary, kernel)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # remove lines, only black rectangles remain
    dilated = cv2.dilate(binary, cv2.getStructuringElement(cv2.MORPH_RECT,(black_rectangle_dilate,black_rectangle_dilate)))

    remove_mask = cv2.bitwise_not(dilated)

    rects_removed = cv2.add(opening, remove_mask)
    steps.append(('opening', rects_removed))

    return (rects_removed, steps)

def detect_rectangles(binary, original):
    steps = []
    height, width = binary.shape
    timings.start('detect_lines')
    (horizontal, vertical) = detect_lines_rust(cv2.bitwise_not(binary), min_line_length)
    timings.end('detect_lines')

    (vertical_lines, horizontal_lines) = reduce_lines(horizontal, vertical, min_distance)
    # TODO: Only remove them if they are touching the border (in the step before or something)
    (horizontal_lines, vertical_lines) = remove_lines_close_to_border(horizontal_lines, vertical_lines, width, height, 0.1 * min_distance)

    # debug
    raw_lines = np.copy(original)
    draw_lines(raw_lines, horizontal, color=(0,255,0))
    draw_lines(raw_lines, vertical, color=(240,150,100))
    steps.append(('raw-lines', raw_lines))

    before_connect = np.copy(original)
    draw_lines(before_connect, vertical_lines + horizontal_lines)
    steps.append(('before-connect', before_connect))

    # add helper lines for borders
    horizontal_lines += [(0,0,width,0), (0,height,width,height)]
    vertical_lines += [(width,height,width,0), (0,height,0,0)]
    (horizontal, vertical) = connect_lines(horizontal_lines, vertical_lines)

    top_left, bottom_left, bottom_right, top_right = find_corners(horizontal, vertical)
    # add given image corners
    top_left.append((0,0))
    bottom_left.append((0,height))
    bottom_right.append((width,height))
    top_right.append((width,0))

    (rectangles,errors) = find_rectangles(top_left, bottom_left, top_right)
    with_lines = np.copy(original)
    for error in errors:
        draw_circle(with_lines, error)
    draw_corners(with_lines, top_left, (0, 90))
    draw_corners(with_lines, top_right, (90, 180))
    draw_corners(with_lines, bottom_right, (180, 270))
    draw_corners(with_lines, bottom_left, (270, 360))

    draw_lines(with_lines, horizontal + vertical)
    steps.append(('lines', with_lines))

    rects_with_color = find_colors_for_rects(rectangles, original)
    return (rects_with_color, steps)

def process_image(original):
    timings.start('full')
    height, width, channels = original.shape
    (preprocessed, steps) = preprocessing(original)

    (rects, second_steps) = detect_rectangles(preprocessed, original)

    steps += second_steps

    output = {
        'height': height,
        'width': width,
        'rectangles': rects,
        'options': {
            'binary_threshold': binary_threshold,
            'min_line_length': min_line_length,
            'min_distance': min_distance,
            'black_rectangle_dilate': black_rectangle_dilate
        }
    }
    drawn = draw_rectangles(rects, height, width)

    steps.append(('drawn', drawn))

    overlay = cv2.addWeighted(original, 0.3, drawn, 0.7,0)
    steps.append(('overlay', overlay))

    side_by_side = np.hstack((original, drawn, overlay))
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(side_by_side,str(len(rects)),(10,500), font, 4,(0,0,0),2,cv2.LINE_AA)
    for index,rect in enumerate(rects):
        cv2.putText(side_by_side,str(index),(rect['x']+4,rect['y']+23), font, 1,(0,0,0),2,cv2.LINE_AA)

    steps.append(('side_by_side', side_by_side))


    timings.end('full')
    return (steps, output)

run_pipeline(process_image)
print('')
print('Time for iteration: %s' % timings.average('full'))
print('Detect lines: %s' % timings.average('detect_lines'))
