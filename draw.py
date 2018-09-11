import cv2, numpy as np
import math

def get_hue(color):
    [[(h,s,v)]] = cv2.cvtColor(np.uint8([[color]]),cv2.COLOR_BGR2HSV)
    return h

def to_bgr(color):
    r,g,b = color
    return b,g,r

debug_colors = False


yellow = to_bgr((255, 243, 0))
blue = to_bgr((0, 102, 181))
red = to_bgr((238, 21, 31))
yellow_hue = get_hue(yellow)
blue_hue = get_hue(blue)
red_hue = get_hue(red)

def draw_lines(img, lines, color = (100, 100, 255)):
    for x1,y1,x2,y2 in lines:
        cv2.line(img,(x1,y1),(x2,y2),color,2)
        cv2.circle(img, (x1,y1), 5, color)

def draw_corners(img, corners, angles, color = (100,255,200)):
    for corner in corners:
        cv2.ellipse(img,corner,(10,10),0,angles[0],angles[1],color,-1)

def draw_points(img, points, color = (255,100,100)):
    for point in points:
        cv2.circle(img, point, 10, color, -1)

def clip_rectangles(rects, img):
    for rect in rects:
        x,y,w,h = rect
        cv2.rectangle(img, (x,y), (x + w, y + h), (255,255,255), -1)


def find_colors_for_rects(rects, source):
    output = []
    for rect_id, rect in enumerate(rects):
        x,y,width,height = rect
        (color, color_name) = get_closest_color(source, rect, rect_id)
        output.append({
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'color': color,
            'color_id': color_name
        })
    return output

def draw_rectangles(rects, height, width):
    blank = np.ones((height,width,3), np.uint8) * 255
    for index, rect in enumerate(rects):
        x = rect['x']
        y = rect['y']
        w = rect['width']
        h = rect['height']
        color = rect['color']

        cv2.rectangle(blank, (x,y), (x + w, y + h), color, -1)
        cv2.rectangle(blank, (x,y), (x + w, y + h), (0,0,0), 5)

    return blank

def get_closest_color(img, rect, rect_id):
    x,y,w,h = rect
    cropped = img[y: y + h, x: x + w]


    avg_color = np.average( np.average(cropped, axis=0), axis=0)
    return find_closest_color(avg_color, rect_id)

def find_closest_color(to_color, rect_id):
    [[(hue,s,v)]] = cv2.cvtColor(np.uint8([[to_color]]),cv2.COLOR_BGR2HSV)
    if debug_colors:
        print('rect %s: saturation %s, value %s' % (rect_id, s,v))
    if s < 62:
        if v > 100:
            return ((255,255,255), 'white')
        if v < 60:
            return ((0,0,0), 'black')

    def get_hue_distance(hue1, hue2):
        small_hue = min(hue1, hue2)
        big_hue = max(hue1, hue2)
        dist1 = big_hue - small_hue
        dist2 = (small_hue + 180) - big_hue
        return min(dist1, dist2)

    distance_yellow = get_hue_distance(hue, yellow_hue)
    distance_blue = get_hue_distance(hue, blue_hue)
    distance_red = get_hue_distance(hue, red_hue)

    distance = distance_yellow
    color = yellow
    color_name = 'yellow'
    if distance_blue < distance:
        distance = distance_blue
        color = blue
        color_name = 'blue'
    if distance_red < distance:
        color = red
        color_name = 'red'

    return (color, color_name)
