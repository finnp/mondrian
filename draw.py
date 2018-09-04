import cv2, numpy as np
import math

def get_hue(color):
    [[(h,s,v)]] = cv2.cvtColor(np.uint8([[color]]),cv2.COLOR_BGR2HSV)
    return h

def to_bgr(color):
    r,g,b = color
    return b,g,r

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

def draw_rectangles(rects, source):
    height, width = source.shape[:2]
    blank = np.ones((height,width,3), np.uint8) * 255
    for index, rect in enumerate(rects):
        x,y,w,h = rect

        color = get_closest_color(source, rect)

        cv2.rectangle(blank, (x,y), (x + w, y + h), color, -1)
        cv2.rectangle(blank, (x,y), (x + w, y + h), (0,0,0), 5)

        # center
        # cv2.circle(blank, (int(x + w/2), int(y + h/2)), 10, (100,100,100), -1)

    return blank

def draw_voronoi(img, rects):

    voronoi = img.copy()

    width, height = img.shape[:2]

    subdiv = cv2.Subdiv2D((0, 0, height, width))

    for rect in rects :
        x,y,w,h = rect
        middle = (round((2*x + w)/2),round((2*y + h)/2))
        subdiv.insert(middle)

    (facets, centers) = subdiv.getVoronoiFacetList([])

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

def get_closest_color(img, rect):
    x,y,w,h = rect

    # w = math.ceil(w/2)
    # h = math.ceil(h/2)
    # x += int(w/4)
    # y += int(h/4)

    cropped = img[y: y + h, x: x + w]

    avg_color = np.average( np.average(cropped, axis=0), axis=0)
    return find_closest_color(avg_color)

def find_closest_color(to_color):
    [[(hue,s,v)]] = cv2.cvtColor(np.uint8([[to_color]]),cv2.COLOR_BGR2HSV)
    if s < 100:
        if v > 120:
            # white
            return (255,255,255)
        if v < 60:
            # black
            return (0,0,0)

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
    if distance_blue < distance:
        distance = distance_blue
        color = blue
    if distance_red < distance:
        color = red

    return color
