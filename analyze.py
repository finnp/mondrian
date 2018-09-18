import json, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

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
paintings = []

for file in files:
    with open(dir + '/' + file) as f:
        data = json.load(f)
    paintings.append(data)
    by_area = get_color_distribution(data)
    rectangles = get_rect_data(data, file)
    rect_data += rectangles
    total = sum(by_area.values())
    if (total > 1.1 or total < 0.9):
        print('Problem with ' + file)
    color_distribution_by_area.append(by_area)
    number_of_rects.append(len(data['rectangles']))

colors = ['red','blue','yellow','black', 'white']

print('Rectangles loaded.')
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
df.index.name = 'id'
df['center_x'] = df['x'] + df['width'] / 2.0
df['center_y'] = df['y'] + df['height'] / 2.0
df['center_x_norm'] = df['center_x'] / df['image_width']
df['center_y_norm'] = df['center_y'] / df['image_height']
df['color'] = df['color_id']
df['longer'] = df[['width','height']].max(axis=1)
df['shorter'] = df[['width','height']].min(axis=1)
df['aspect_max_min'] = df['longer'] / df['shorter']
df['aspect'] = df['width'] / df['height']

images = df.groupby('image_file').agg({'color': 'unique'})
images['color'] = images['color'].apply(set)
total = len(images)
print('total', total)
for color in colors:
    images[color] = images['color'].apply(lambda r: color in r)
    l = len(images[images[color]])
    print(color, l, float(l) / total * 100)

print('Conditional probabilities, given color column')
# Immer noch nicht so aussagkräftig :)
l = []
for color in colors:
    l.append(images[images[color]].sum() / float(len(images[images[color]]))*100)
print(pd.DataFrame(l, index=colors))
images['count'] = images['color'].apply(len)
print('Number of different colors')
print(images.groupby('count').count()['color'])


without_white = df[df['color'] != 'white']
ax = without_white.plot.scatter(x='center_x_norm', y='center_y_norm',c=without_white['color'])
grouped_by_color = df.groupby('color')
mean_points = grouped_by_color.mean()
std_points = grouped_by_color.std()
df.to_csv('rectangles.csv')

for color in ['red','blue','yellow','black']:
    c_x = mean_points['center_x_norm'][color]
    c_y = mean_points['center_y_norm'][color]
    s_x = std_points['center_x_norm'][color]
    s_y = std_points['center_y_norm'][color]
    plt.plot(c_x,c_y,'x',c=color)
    std = np.sqrt(s_x**2 + s_y**2)
    ax.add_artist(plt.Circle((c_x, c_y), std, color=color, Fill=False))

plt.title('Center of rectangles, normalized by image height/width')
plt.gca().invert_yaxis()
plt.savefig(out_dir + '/points.png')
plt.close()


white_only = df[df['color'] == 'white']
ax = white_only.plot.scatter(x='center_x_norm', y='center_y_norm')
plt.title('Center of white rectangles, normalized by image height/width')
c_x = mean_points['center_x_norm']['white']
c_y = mean_points['center_y_norm']['white']
s_x = std_points['center_x_norm']['white']
s_y = std_points['center_y_norm']['white']
plt.plot(c_x,c_y,'x',c='black')
std = np.sqrt(s_x**2 + s_y**2)
ax.add_artist(plt.Circle((c_x, c_y), std, color='black', Fill=False))
plt.gca().invert_yaxis()
plt.savefig(out_dir + '/white-points.png')
plt.close()


# https://seaborn.pydata.org/tutorial/distributions.html
# https://en.wikipedia.org/wiki/Kernel_density_estimation
for color in colors:
    with sns.axes_style('white'):
        g = sns.jointplot(
            x="center_x_norm",
            y="center_y_norm",
            xlim=(0,1),
            ylim=(0,1),
            data=df[df['color'] == color],
            cbar=True,
            vmin=0,
            vmax=3,
            kind="kde")
        plt.title(color)
        g.plot_joint(plt.scatter, c="w", s=30, linewidth=1, marker="+")
    plt.gca().invert_yaxis()
    plt.savefig(out_dir + '/kernel-density-' + color + '.png')
    plt.close()

g = sns.FacetGrid(df, col="color",legend_out=True,xlim=(0,1),ylim=(0,1),col_wrap=2)
g.map(sns.kdeplot, "center_x_norm", "center_y_norm",shade=True,cbar=False,vmin=0,vmax=2.25)
plt.gca().invert_yaxis()
plt.savefig(out_dir + '/kernel-densities.png')
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

# histogram(df['aspect_max_min'], 20)
x = df[df['aspect_max_min'] < 3]['aspect_max_min']
sns.set_style("darkgrid")
sns.kdeplot(x, shade=True, cut=0)
sns.rugplot(x);
plt.title('Aspect ratio longer side to shorter')
plt.savefig(out_dir + '/aspect-max-min-rects.png')
plt.close()

width = df[df['aspect'] > 1]['aspect']
height = 1 / df[df['aspect'] < 1]['aspect']
sns.set_style("darkgrid")
sns.kdeplot(width, shade=True, cut=0, label='width/height')
sns.kdeplot(height, shade=True, cut=0,label='height/width')
sns.rugplot(width);
sns.rugplot(height);
plt.title('Aspect ratio width to height')
plt.savefig(out_dir + '/aspect-rects.png')
plt.close()
