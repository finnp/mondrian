import cv2, numpy as np
import sys
import imutils
import os
import json
import datetime

retr_type = cv2.RETR_LIST
contour_algorithm = cv2.CHAIN_APPROX_SIMPLE

def to_opencv_color(color):
    r,g,b = color
    return (b,g,r)

yellow = (255, 243, 0)
blue = (0, 102, 181)
red = (238, 21, 31)
white = (255, 255, 255)
colors = [to_opencv_color(yellow), to_opencv_color(blue), to_opencv_color(red), to_opencv_color(white)]

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

def find_closest_color(to_color):
    current_distance = 500
    current_color = (255, 255, 255)
    for from_color in colors:
        new_distance = np.linalg.norm(np.array(from_color) - to_color)
        if (new_distance < current_distance):
            current_color = from_color
            current_distance = new_distance
    return current_color

def draw_rectangles(rects, source):
    height, width = source.shape[:2]
    blank = np.zeros((height,width,3), np.uint8)
    for index, rect in enumerate(rects):
        x,y,w,h = rect

        cropped = source[y: y + h, x: x + w]
        avg_color = np.average( np.average(cropped, axis=0), axis=0)
        print("avg", avg_color)
        color = avg_color
        color = find_closest_color(avg_color)
        print("closest", color)

        cv2.rectangle(blank, (x,y), (x + w, y + h), color, -1)
    return blank


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

    b,g,r = cv2.split(original)
    _, binary = cv2.threshold(original, threshold_value, 255, cv2.THRESH_BINARY)

    b_t,g_t,r_t = cv2.split(binary)

    max = cv2.max(cv2.max(b_t, g_t), r_t)

    opening = cv2.morphologyEx(max, cv2.MORPH_OPEN, kernel)

    draw_black_border(opening)

    file_without_ending = file_name[:-len('.' + image_type)]
    output_filename = output_dir + '/' + file_without_ending + '-binary'
    cv2.imwrite(output_filename  + '.jpg', binary)
    output_filename = output_dir + '/' + file_without_ending + '-max'
    cv2.imwrite(output_filename  + '.jpg', max)
    output_filename = output_dir + '/' + file_without_ending + '-open' # best so far i think
    cv2.imwrite(output_filename  + '.jpg', opening)

    rects, polygons = find_contours(opening)

    save_rects(rects, output_dir + '/' + file_without_ending + '.json')

    drawn = draw_rectangles(rects, original)
    output_filename = output_dir + '/' + file_without_ending + '-drawn' # best so far i think
    cv2.imwrite(output_filename  + '.jpg', drawn)

    cv2.drawContours(original,polygons,-1,(0,255,0),3)
    output_filename = output_dir + '/' + file_without_ending + '-marked'
    cv2.imwrite(output_filename  + '.jpg', original)

    #
    #     with open(output_filename + '.json', 'w') as fp:
    #         json.dump(metadata, fp)

files = os.listdir(input_dir)
files = list(filter(lambda f: f[-len(image_type):] == 'jpg', files))
total = len(files)

for index, file_name in enumerate(files):
    print('processing ' + str(index + 1) + '/' + str(total), file_name)
    process_image(file_name)
