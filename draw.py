import cv2, numpy as np

def to_opencv_color(color):
    r,g,b = color
    return (b,g,r)

yellow = (255, 243, 0)
blue = (0, 102, 181)
red = (238, 21, 31)
white = (255, 255, 255)
colors = [to_opencv_color(yellow), to_opencv_color(blue), to_opencv_color(red), to_opencv_color(white)]


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

    cropped = img[y: y + h, x: x + w]
    avg_color = np.average( np.average(cropped, axis=0), axis=0)
    return find_closest_color(avg_color)

def find_closest_color(to_color):
    current_distance = 500
    current_color = (255, 255, 255)
    for from_color in colors:
        new_distance = np.linalg.norm(np.array(from_color) - to_color)
        if (new_distance < current_distance):
            current_color = from_color
            current_distance = new_distance
    return current_color
