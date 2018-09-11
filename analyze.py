import json, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dir = 'detected'
out_dir = 'graphs'

files = os.listdir(dir)

def get_rect_data(data, file):
    width = data['width']
    height = data['height']
    rects = []
    for rect in data['rectangles']:
        rect['image_width'] = width
        rect['image_height'] = height
        rect['image_file'] = file
        rects.append(rect)
    return rects


def get_color_distribution(data):
    full_area = float(data['height'] * data['width'])
    colors = {
        'black': 0,
        'white': 0,
        'blue': 0,
        'yellow': 0,
        'red': 0
    }
    for rect in data['rectangles']:
        rect_area = rect['height'] * rect['width']
        colors[rect['color_id']] += float(rect_area) / full_area
    return colors

color_distribution_by_area = []
number_of_rects = []
rect_data = []

for file in files:
    print(file)
    with open(dir + '/' + file) as f:
        data = json.load(f)
    by_area = get_color_distribution(data)
    rect_data += get_rect_data(data, file)
    total = sum(by_area.values())
    if (total > 1.1 or total < 0.9):
        print('Problem with ' + file)
    color_distribution_by_area.append(by_area)
    number_of_rects.append(len(data['rectangles']))

df = pd.DataFrame(color_distribution_by_area)
df.boxplot()
plt.savefig(out_dir + '/colors.png')
plt.close()

axes = df.boxplot(column=['red', 'blue', 'yellow'], return_type='axes')
axes.set_ylim(0, 0.3)
plt.savefig(out_dir + '/colors-rby.png')
plt.close()

df['colors'] = df['red'] + df['blue'] + df['yellow']
df['non-colors'] = df['white'] + df['black']
df.boxplot(column=['colors', 'non-colors'])
plt.savefig(out_dir + '/colors-non-colors.png')
plt.close()

def histogram(df, bins):
    df.hist(bins=np.arange(bins + 1) - 0.5)
    plt.xticks(range(bins))
    plt.xlim([-1, bins])

df = pd.DataFrame({'Number of rectangles': number_of_rects})
histogram(df, 20)
plt.savefig(out_dir + '/n-rects.png')
plt.close()

df = pd.DataFrame(rect_data)
df['center_x'] = df['x'] + df['width'] / 2.0
df['center_y'] = df['y'] + df['height'] / 2.0
df['color'] = df['color_id']
df['longer'] = df[['width','height']].max(axis=1)
df['shorter'] = df[['width','height']].min(axis=1)
df['aspect_max_min'] = df['longer'] / df['shorter']
df['aspect'] = df['width'] / df['height']

without_white = df[df['color'] != 'white']
without_white.plot.scatter(x='center_x', y='center_y',c=without_white['color'])
plt.title('Center of rectangles, normalized by image height/width')
plt.savefig(out_dir + '/points.png')
plt.close()

df.plot.scatter(x='shorter', y='longer', s=1, c='black')
plt.title('Rectangle longer to shorter side (not normalized)')
plt.plot([0, 618], [0, 1000], 'k-', alpha=0.3, label='golden ratio', c='red')
plt.plot([0, 414], [0, 1000], 'k-', alpha=0.3, label='silver ratio')
plt.plot([0, 707], [0, 1000], 'k-', alpha=0.3, label='sqrt(2)', c='blue')
plt.plot([0, 1000], [0, 1000], 'k-', alpha=0.7, label='1')
plt.legend()
plt.savefig(out_dir + '/longer-x-shorter.png')
plt.close()

df[df['color'] == 'white'].plot.scatter(x='center_x', y='center_y')
plt.title('Center of white rectangles, normalized by image height/width')
plt.savefig(out_dir + '/white-points.png')
plt.close()

histogram(df['aspect_max_min'], 20)
plt.title('Aspect ratio longer side to shorter')
plt.savefig(out_dir + '/aspect-max-min-rects.png')
plt.close()

histogram(df['aspect'], 20)
plt.title('Aspect ratio width to height')
plt.savefig(out_dir + '/aspect-rects.png')
plt.close()
