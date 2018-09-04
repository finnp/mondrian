import cv2, numpy as np
import sys
import imutils
import datetime
from lines import connect_lines, reduce_lines, detect_lines, find_corners, find_rectangles
from draw import draw_rectangles, draw_lines, draw_points, draw_corners, clip_rectangles
from files import process_pipeline

retr_type = cv2.RETR_LIST
contour_algorithm = cv2.CHAIN_APPROX_SIMPLE

threshold_value = 110

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(11,11))

def find_contours (img):
    _, contours, _ = cv2.findContours(img.copy(), retr_type, contour_algorithm)
    # contours = list(filter(lambda cont: cv2.contourArea(cont) > min_ticket_size, contours))
    rects = []
    polygons = []
    for cont in contours:
        polygon = cv2.approxPolyDP(cont, 1, True).copy().reshape(-1, 2)
        polygon = cv2.convexHull(polygon)
        area = cv2.contourArea(polygon)
        rect = cv2.boundingRect(polygon)
        rects.append(rect)
        polygons.append(polygon)

    return (rects, polygons)

def draw_black_border(img):
    height, width = img.shape[:2]
    cv2.rectangle(img, (0,0), (width, height), (0, 0, 0))

def process_image(original):
    steps = []
    height, width, channels = original.shape

    blurred = cv2.blur(original,(5,5))

    b_t,g_t,r_t = cv2.split(blurred)

    max = cv2.max(cv2.max(b_t, g_t), r_t)

    min = cv2.min(cv2.min(b_t, g_t), r_t)

    _, deviation = cv2.threshold(max - min, 25, 255, cv2.THRESH_BINARY)

    steps.append(('deviation', deviation))

    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(max)
    print(minVal)

    # 200,200,200
    # 100,200,100 -> 100

    steps.append(('max', max))

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast_fixed = clahe.apply(max)

    # contrast_fixed = cv2.equalizeHist(max)

    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(contrast_fixed)
    print(minVal)

    steps.append(('contrast', contrast_fixed))

    color_contrast = cv2.max(contrast_fixed, deviation)

    steps.append(('color-contrast', color_contrast))

    _, binary = cv2.threshold(color_contrast, threshold_value, 255, cv2.THRESH_BINARY)
    steps.append(('binary', binary))

    max = binary

    opening = cv2.erode(max, kernel)

    # remove lines, only black rectangles remain
    dilated = cv2.dilate(max, cv2.getStructuringElement(cv2.MORPH_RECT,(29,29)))

    remove_mask = cv2.bitwise_not(dilated)

    opening = cv2.max(opening, remove_mask)

    with_lines = np.copy(original)

    steps.append(('opening', opening))

    (horizontal, vertical) = detect_lines(cv2.bitwise_not(opening))

    min_distance = width * 0.03 # minimal distance for lines to be considered distinct

    (vertical_lines, horizontal_lines) = reduce_lines(horizontal, vertical, min_distance)
    before_connect = np.copy(original)
    draw_lines(before_connect, horizontal + vertical, color=(255,255,255))
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

    rects, polygons = find_contours(opening)
    drawn = draw_rectangles(rectangles, binary)

    steps.append(('drawnn', drawn))

    overlay = cv2.addWeighted(original, 0.3, drawn, 0.7,0)
    steps.append(('overlay', overlay))

    return steps

process_pipeline(process_image)
