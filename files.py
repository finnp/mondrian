import os
import cv2
import json
import sys

input_dir = 'image-selection'
output_dir = 'output'
image_type = 'jpg'
detected_dir = 'detected'

def process_pipeline(process_image):
    detected = [file[:-5] for file in os.listdir(detected_dir)]
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            print('Running test mode')
            files = [id+ '.jpg' for id in detected]
        else:
            files = [name + '.jpg' for name in sys.argv[1:]]
    else:
        files = os.listdir(input_dir)
        files = list(filter(lambda f: f[-len(image_type):] == 'jpg', files))
    total = len(files)

    detected_data = dict([(id, read_data(detected_dir + '/' + id)) for id in detected])

    for index, file_name in enumerate(files):
        id = file_name[:-4]
        print('processing ' + str(index + 1) + '/' + str(total), id)
        img = cv2.imread(input_dir + '/' + file_name)
        (outputs, data) = process_image(img)

        if id in detected_data:
            check_data(detected_data[id], data)

        file_without_ending = file_name[:-len('.' + image_type)]
        data_dir = output_dir + '/data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        save_data(data, data_dir + '/' + file_without_ending + '.json')
        for step_index, (type, img) in enumerate(outputs):
            subdir = output_dir + '/' + str(step_index) + '-' + type
            if index == 0:
                if not os.path.exists(subdir):
                    os.makedirs(subdir)
            output_filename = subdir + '/' + file_without_ending + '.jpg'
            cv2.imwrite(output_filename, img)

def save_data(data, filename):
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4)

def read_data(filename):
    if (filename[-5:] != '.json'):
        filename += '.json'
    with open(filename) as f:
        return json.load(f)

def print_issue(text, got, expected):
    print('\t🚨 %s, got %s, expected %s' %(text, got, expected))

def check_data(proven, data):
    proven_rects = proven['rectangles']
    data_rects = data['rectangles']
    len_proven = len(proven_rects)
    len_data = len(data_rects)
    if (len_proven != len_data):
        print_issue('Wrong number of rectangles', len_data, len_proven)
        return
    for index, rect in enumerate(data_rects):
        rect_proven = proven_rects[index]
        if rect['color_id'] != rect_proven['color_id']:
            print_issue('Wrong color', rect['color_id'], rect_proven['color_id'])
