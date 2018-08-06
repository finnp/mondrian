import cv2, numpy as np
import sys
import imutils
import datetime
from lines import connect_lines, reduce_lines, detect_lines
from draw import draw_rectangles, draw_lines
from files import process_pipeline

retr_type = cv2.RETR_LIST
contour_algorithm = cv2.CHAIN_APPROX_SIMPLE

threshold_value = 50

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))

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
    height, width, channels = original.shape

    b,g,r = cv2.split(original)
    _, binary = cv2.threshold(original, threshold_value, 255, cv2.THRESH_BINARY)

    b_t,g_t,r_t = cv2.split(binary)

    max = cv2.max(cv2.max(b_t, g_t), r_t)

    opening = cv2.morphologyEx(max, cv2.MORPH_OPEN, kernel)

    # adjust these numbers
    with_lines = np.copy(original)
    edges = cv2.Canny(opening, 50, 150)

    (horizontal, vertical) = detect_lines(cv2.bitwise_not(opening))

    min_distance = width * 0.03 # minimal distance for lines to be considered distinct

    (vertical_lines, horizontal_lines) = reduce_lines(horizontal, vertical, min_distance)

    # add helper lines for borders
    horizontal_lines += [(0,0,width,0), (0,height,width,height)]
    vertical_lines += [(0,0,0,height), (width,0,width,height)]

    connected_lines = connect_lines(horizontal_lines, vertical_lines)
    draw_lines(with_lines, connected_lines)

    # draw_lines(with_lines, connected_lines)

    draw_black_border(opening)

    rects, polygons = find_contours(opening)
    drawn = draw_rectangles(rects, original)

    cv2.drawContours(original,polygons,-1,(0,255,0),3)

    return [
        (with_lines, 'lines'),
        (edges, 'edges'),
        (binary, 'binary'),
        (max, 'max'),
        (opening, 'open'),
        (drawn, 'drawn'),
        (original, 'marked')
    ]

process_pipeline(process_image)
