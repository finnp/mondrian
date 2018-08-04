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

def get_closest_color(img, rect):
    x,y,w,h = rect

    cropped = img[y: y + h, x: x + w]
    avg_color = np.average( np.average(cropped, axis=0), axis=0)
    return find_closest_color(avg_color)

def draw_voronoi(img, rects):

    voronoi = img.copy()

    width, height = img.shape[:2]

    subdiv = cv2.Subdiv2D((0, 0, height, width))

    for rect in rects :
        x,y,w,h = rect
        middle = (round((2*x + w)/2),round((2*y + h)/2))
        subdiv.insert(middle)

    ( facets, centers) = subdiv.getVoronoiFacetList([])

    for i in range(0,len(facets)) :
        ifacet_arr = []
        for f in facets[i] :
            ifacet_arr.append(f)

        color = get_closest_color(img, rects[i])

        ifacet = np.array(ifacet_arr, np.int)


        cv2.fillConvexPoly(voronoi, ifacet, color);
        ifacets = np.array([ifacet])
        cv2.polylines(voronoi, ifacets, True, (0, 0, 0), 1)
        cv2.circle(voronoi, (centers[i][0], centers[i][1]), 3, (0, 0, 0), -1)
    return voronoi

def draw_rectangles(rects, source):
    height, width = source.shape[:2]
    blank = np.zeros((height,width,3), np.uint8)
    for index, rect in enumerate(rects):
        x,y,w,h = rect

        color = get_closest_color(source, rect)

        cv2.rectangle(blank, (x,y), (x + w, y + h), color, -1)
        middle = (round((2*x + w)/2),round((2*y + h)/2))
        cv2.circle(blank, middle, 4, (0, 0 ,0), -1)
        corner_u_l = x,y
        corner_u_r = x + w,y
        corner_d_l = x,y+h
        corner_d_r = (x + w, y + h)
        cv2.circle(blank, corner_u_l, 3, (0, 255 ,0), -1)
        cv2.circle(blank, corner_u_r, 3, (0, 255 ,0), -1)
        cv2.circle(blank, corner_d_l, 3, (0, 255 ,0), -1)
        cv2.circle(blank, corner_d_r, 3, (0, 255 ,0), -1)

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
    already_seen = set()
    reduced_lines = []

    for index, line in enumerate(lines):
        x1,y1,x2,y2 = line[0]
        # cv2.line(with_lines,(x1,y1),(x2,y2),(0,0,255),2)
        if index in already_seen:
            continue
        if (abs(y1-y2) > abs(x1-x2)):
            # vertical
            for other_index, other_line in enumerate(lines):
                x1_other,y1_other,x2_other,y2_other = other_line[0]
                if (abs(x1 - x1_other) < 50):
                    if (y2_other < y2):
                        y2 = y2_other
                    if (y1_other > y1):
                        y1 = y1_other

                    already_seen.add(other_index)
        else:
            #horizontal
            for other_index, other_line in enumerate(lines):
                x1_other,y1_other,x2_other,y2_other = other_line[0]
                if (abs(y1 - y1_other) < 50):
                    already_seen.add(other_index)

        reduced_lines.append((x1,y1,x2,y2))

    for x1,y1,x2,y2 in reduced_lines:
        line_color = (np.random.randint(200, 255),np.random.randint(200, 255),np.random.randint(200,255))
        cv2.line(with_lines,(x1,y1),(x2,y2),line_color,2)
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

    voronoi = draw_voronoi(original, rects)
    save_img(voronoi, 'voronoi')

    cv2.drawContours(original,polygons,-1,(0,255,0),3)
    save_img(original, 'marked')

files = os.listdir(input_dir)
files = list(filter(lambda f: f[-len(image_type):] == 'jpg', files))
total = len(files)

for index, file_name in enumerate(files):
    print('processing ' + str(index + 1) + '/' + str(total), file_name)
    process_image(file_name)
