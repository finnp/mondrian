import json, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from itertools import combinations


dir = 'detected'
out_dir = 'graphs'

files = os.listdir(dir)

def load_kdtree():
    data = open('KdTreeSizes.txt', 'r').read().split('\n')
    data = [d.split(';') for d in data]

    output = []
    for run in data:
        run = run[1:len(run)-1]
        run = [float(r) for r in run]
        output.append(run)

    return output


def get_rect_data(data, file):
    width = data['width']
    height = data['height']
    rects = []
    for index, rect in enumerate(data['rectangles']):
        rect['index'] = index
        rect['image_width'] = width
        rect['image_height'] = height
        rect['image_file'] = file
        rects.append(rect)
    return rects

def get_all_points(rect):
    points = []
    for i in range(rect['width']):
        for j in range(rect['height']):
            points.append({
                'x': rect['x'] + i,
                'y': rect['y'] + j,
                'color': rect['color_id']
            })
    return points

def get_number_of_rectangle_by_color(data):
    colors = {
        'black': 0,
        'white': 0,
        'blue': 0,
        'yellow': 0,
        'red': 0
    }
    for rect in data['rectangles']:
        colors[rect['color_id']] += 1
    return colors


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
color_distribution_by_number = []
number_of_rects = []
rect_data = []
paintings = []

for file in files:
    with open(dir + '/' + file) as f:
        data = json.load(f)
    paintings.append(data)
    by_area = get_color_distribution(data)
    by_number = get_number_of_rectangle_by_color(data)
    rectangles = get_rect_data(data, file)
    rect_data += rectangles
    total = sum(by_area.values())
    if (total > 1.1 or total < 0.9):
        print('Problem with ' + file)
    color_distribution_by_area.append(by_area)
    color_distribution_by_number.append(by_number)
    number_of_rects.append(len(data['rectangles']))


# print('Calculate all points')
# all_points = []
# for rect in rect_data:
#     all_points += get_all_points(rect)
#
# p_df = pd.DataFrame(all_points)
# p_df.to_csv('points.csv')
#
# print('done points')

colors = ['red','blue','yellow','black', 'white']

print('Rectangles loaded.')

plt.rcParams.update({
'axes.labelsize': 'xx-large',
'xtick.labelsize': 'xx-large',
'ytick.labelsize': 'x-large',
})

# color distribution by area

df = pd.DataFrame(color_distribution_by_area)
ax = df.boxplot()
ax.set_ylabel('Proportion of total area')
plt.savefig(out_dir + '/colors_area.png')
plt.close()

axes = df.boxplot(column=['red', 'blue', 'yellow'], return_type='axes')
axes.set_ylim(0, 0.6)
axes.set_ylabel('Proportion of total area')
plt.savefig(out_dir + '/colors-rby.png')
plt.close()

df['colors'] = df['red'] + df['blue'] + df['yellow']
df['non-colors'] = df['white'] + df['black']
print(df['colors'].mean()*100, df['colors'].std()*100)
print(df['non-colors'].mean()*100, df['non-colors'].std()*100)
for color in colors:
    print(color, df[color].median()*100)
    print(color, df[color].mean() * 100, df[color].std() * 100)
ax = df.boxplot(column=['colors', 'non-colors'])
ax.set_ylabel('Proportion of total area')
ax.set_ylim(0, 1)
plt.savefig(out_dir + '/colors-non-colors.png')
plt.close()

# color distribution by number of rectangles

df = pd.DataFrame(color_distribution_by_number)
ax = df.boxplot()
ax.set_ylabel('Number of rectangles')
plt.savefig(out_dir + '/colors_n.png')
plt.close()

axes = df.boxplot(column=['red', 'blue', 'yellow'], return_type='axes')
axes.set_ylabel('Number of rectangles')
plt.savefig(out_dir + '/colors-rby-n.png')
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
df['size'] = df['width'] * df['height']

images = df.groupby('image_file').agg({'color': 'unique', 'color_id': 'count'})
print(images[images['color_id'] == 5])
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

fig, ax = plt.subplots()
df['color'].value_counts().plot(ax=ax, kind='bar')
plt.savefig(out_dir + '/n-by-color.png')
plt.close()

df.boxplot(by='color',column='size')
plt.savefig(out_dir + '/size-by-color.png')
plt.close()

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
g.map(plt.scatter, "center_x_norm", "center_y_norm",marker='x',color='white',alpha=0.7)
# cbar_ax = g.fig.add_axes([1.015,0.13, 0.015, 0.8])
# plt.colorbar(cbar_ax)
plt.gca().invert_yaxis()
plt.savefig(out_dir + '/kernel-densities.png')
plt.close()

df.plot.scatter(x='shorter', y='longer', s=1, c='black')
plt.plot([0, 618], [0, 1000], 'k-', alpha=0.3, label='golden ratio', c='red')
plt.plot([0, 414], [0, 1000], 'k-', alpha=0.3, label='silver ratio')
plt.plot([0, 707], [0, 1000], 'k-', alpha=0.3, label='sqrt(2)', c='blue')
plt.plot([0, 1000], [0, 1000], 'k-', alpha=0.7, label='1')
plt.legend(fontsize='xx-large')
plt.savefig(out_dir + '/longer-x-shorter.png')
plt.close()

# histogram(df['aspect_max_min'], 20)

rand_df = pd.DataFrame(np.random.randint(0,1000,size=(10000, 2)), columns=list('AB'))
rand_df['aspect_max_min'] = rand_df[['A','B']].max(axis=1) / rand_df[['A','B']].min(axis=1)
x = df[df['aspect_max_min'] <= 3]['aspect_max_min']
y = rand_df[rand_df['aspect_max_min'] <= 3]['aspect_max_min']

kd_data = np.array(load_kdtree()).flatten()
kd_df = pd.DataFrame(kd_data[0:1300], columns=['aspect_max_min'])
kd = kd_df[kd_df['aspect_max_min'] <= 3]['aspect_max_min']

sns.set_style("darkgrid")
sns.kdeplot(x, shade=True, cut=0,gridsize=100,label="Mondrian rectangles")
sns.kdeplot(y, shade=True, cut=0,gridsize=100,label="Random rectangles")
sns.kdeplot(kd, shade=True, cut=0,gridsize=100,label="Kd rectangles")
# plt.xlim((1,20))
sns.rugplot(x);
plt.title('Aspect ratio r longer side to shorter r < 3')
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
