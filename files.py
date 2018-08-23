import os
import cv2
import json
import sys

input_dir = 'img'
output_dir = 'output'
image_type = 'jpg'

def process_pipeline(process_image):
    if len(sys.argv) > 1:
        files = [name + '.jpg' for name in sys.argv[1:]]
    else:
        files = os.listdir(input_dir)
        files = list(filter(lambda f: f[-len(image_type):] == 'jpg', files))
    total = len(files)

    for index, file_name in enumerate(files):
        print('processing ' + str(index + 1) + '/' + str(total), file_name)
        img = cv2.imread(input_dir + '/' + file_name)
        outputs = process_image(img)
        file_without_ending = file_name[:-len('.' + image_type)]
        for img, type in outputs:
            output_filename = output_dir + '/' + type + '-' + file_without_ending
            cv2.imwrite(output_filename  + '.jpg', img)

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
