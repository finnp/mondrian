import os
import cv2
import json
import sys

input_dir = 'image-selection'
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
        for step_index, (type, img) in enumerate(outputs):
            subdir = output_dir + '/' + str(step_index) + '-' + type
            if index == 0:
                if not os.path.exists(subdir):
                    os.makedirs(subdir)
            output_filename = subdir + '/' + file_without_ending + '.jpg'
            cv2.imwrite(output_filename, img)

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
