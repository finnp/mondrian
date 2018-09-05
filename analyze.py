import json, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dir = 'detected'
out_dir = 'graphs'

files = os.listdir(dir)

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

for file in files:
    print(file)
    with open(dir + '/' + file) as f:
        data = json.load(f)
    by_area = get_color_distribution(data)
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
