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

for file in files:
    print(file)
    with open(dir + '/' + file) as f:
        data = json.load(f)
    img = draw_rectangles(data['rectangles'], data['height'], data['width'])
    file_without_ending = file[:-len('.json')]
    original = cv2.imread(image_dir + '/' + file_without_ending + '.jpg')
    side_by_side = np.hstack((original, img))
    cv2.putText(side_by_side,str(len(data['rectangles'])),(10,500), font, 4,(0,0,0),2,cv2.LINE_AA)
    cv2.imwrite(out_dir + '/' + file_without_ending + '.jpg', side_by_side)
