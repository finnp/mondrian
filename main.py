import cv2, numpy as np
import sys
import imutils
import os
import json
import datetime

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
    cv2.rectangle(img, (0,0), (width, height), (0, 255, 0))

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
