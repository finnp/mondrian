import os
import json
import cv2
import numpy as np
from draw import draw_rectangles

dir = 'detected'
out_dir = 'detected-output'
image_dir = 'image-selection'
font = cv2.FONT_HERSHEY_SIMPLEX

files = os.listdir(dir)

def get_center(rect):
    return (int(rect['x'] + rect['width'] / 2.0), int(rect['y'] + rect['height'] / 2.0))

for file in files:
    print(file)
    with open(dir + '/' + file) as f:
        data = json.load(f)

    img = draw_rectangles(data['rectangles'], data['height'], data['width'])
    for [a,b] in data['edges']:
        rect_a = data['rectangles'][a]
        center_a = get_center(rect_a)
        rect_b = data['rectangles'][b]
        center_b = get_center(rect_b)
        cv2.line(img, center_a, center_b, 5)

    file_without_ending = file[:-len('.json')]
    # original = cv2.imread(image_dir + '/' + file_without_ending + '.jpg')
    # side_by_side = np.hstack((original, img))
    # cv2.putText(side_by_side,str(len(data['rectangles'])),(10,500), font, 4,(0,0,0),2,cv2.LINE_AA)
    cv2.imwrite(out_dir + '/' + file_without_ending + '.jpg', img)
