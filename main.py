import cv2, numpy as np
import sys
import imutils
import os
import json
import datetime
from lines import connect_lines, reduce_lines
from draw import draw_rectangles

retr_type = cv2.RETR_LIST
contour_algorithm = cv2.CHAIN_APPROX_SIMPLE

input_dir = 'img'
output_dir = 'output'
image_type = 'jpg'

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

def save_rects(rects, filename):
    rectangles = []
    for index, rect in enumerate(rects):
        x,y,w,h = rect
        rectangles.append({
            'x': x,
            'y': y,
            'width': w,
            'height': h
        })
    with open(filename, 'w') as fp:
        json.dump(rectangles, fp)

def process_image(file_name):
    original = cv2.imread(input_dir + '/' + file_name)

    height, width, channels = original.shape

    b,g,r = cv2.split(original)
    _, binary = cv2.threshold(original, threshold_value, 255, cv2.THRESH_BINARY)

    b_t,g_t,r_t = cv2.split(binary)

    max = cv2.max(cv2.max(b_t, g_t), r_t)

    opening = cv2.morphologyEx(max, cv2.MORPH_OPEN, kernel)

    # adjust these numbers
    with_lines = np.copy(original)
    edges = cv2.Canny(opening, 50, 150)
    lines = cv2.HoughLinesP(
        cv2.bitwise_not(opening),
        rho = 1,
        theta = np.pi / 2,
        threshold=50,
        minLineLength=120,
        maxLineGap=10
    )

    (vertical_lines, horizontal_lines) = reduce_lines(lines)

    # add helper lines for borders
    horizontal_lines += [(0,0,width,0), (0,height,width,height)]
    vertical_lines += [(0,0,0,height), (width,0,width,height)]

    connected_lines = connect_lines(horizontal_lines, vertical_lines)

    for x1,y1,x2,y2 in connected_lines:
        cv2.line(with_lines,(x1,y1),(x2,y2),(100, 100, 255),2)
        cv2.circle(with_lines, (x1,y1), 5, (255,255,255))

    draw_black_border(opening)

    file_without_ending = file_name[:-len('.' + image_type)]
    def save_img(img, type):
        output_filename = output_dir + '/' + type + '-' + file_without_ending
        cv2.imwrite(output_filename  + '.jpg', img)

    save_img(with_lines, 'lines')
    save_img(edges, 'edges')
    save_img(binary, 'binary')
    save_img(max, 'max')
    save_img(opening, 'open') # best so far

    rects, polygons = find_contours(opening)

    save_rects(rects, output_dir + '/' + file_without_ending + '.json')

    drawn = draw_rectangles(rects, original)
    save_img(drawn, 'drawn')

    cv2.drawContours(original,polygons,-1,(0,255,0),3)
    save_img(original, 'marked')

files = os.listdir(input_dir)
files = list(filter(lambda f: f[-len(image_type):] == 'jpg', files))
total = len(files)

for index, file_name in enumerate(files):
    print('processing ' + str(index + 1) + '/' + str(total), file_name)
    process_image(file_name)
