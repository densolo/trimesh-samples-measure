import lxml
import trimesh
import os

path = os.path.join(os.path.dirname(__file__), "File.3mf")
assert os.path.exists(path)
mesh = trimesh.load_mesh(path)

import numpy as np
from math import sin, cos, atan, pi, sqrt, pow

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.lines as mlines
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import matplotlib.gridspec as gridspec

X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2

def rotate_xy(x_arr, y_arr, degree):
    return rotate_xy_rad(x_arr, y_arr, degree * pi / 180)


def rotate_xy_rad(x_arr, y_arr, r):
    print("rotate: {} degree".format(r*180/pi))

    for i in range(len(x_arr)):
        x = x_arr[i]
        y = y_arr[i]

        cr = cos(r)
        sr = sin(r)
        x1 = x * cr - y * sr
        y1 = y * cr + x * sr
        x_arr[i] = x1
        y_arr[i] = y1


def rotate_points_xy_rad(points, dim1, dim2, r):
    print("rotate {}{}: {} degree".format(dim1, dim2, r*180/pi))

    for i in range(len(points)):
        p = list(points[i])
        x = p[dim1]
        y = p[dim2]

        cr = cos(r)
        sr = sin(r)
        x1 = x * cr - y * sr
        y1 = y * cr + x * sr

        p[dim1] = x1
        p[dim2] = y1
        points[i] = p


def move_zero(x_arr):
    a, b = find_limit(x_arr)
    av = (b + a)/2
    x_arr[:] = [x - av for x in x_arr]


def find_limit(arr):
    if not arr:
        return 0, 0 
    arr = sorted(arr)
    return arr[0], arr[-1]


def find_limit_indexes(arr):
    if not arr:
        return 0, 0 
    arr = sorted(enumerate(arr), key=lambda it: it[1])
    return arr[0][0], arr[-1][0]


def distance(p1, p2):
    return sqrt(sum([pow(p2[i] - p1[i], 2) for i in range(3)]))


def split_point_buckets(points, dim, dist):
    points = sorted(points, key=lambda p: p[dim])
    
    prev_p = points[0]
    cur_bucket = [prev_p]
    buckets = [cur_bucket]

    for p in points[1:]:
        if p[dim] - prev_p[dim] > dist:
            cur_bucket = []
            buckets.append(cur_bucket)
        cur_bucket.append(p)
        prev_p = p

    return buckets


def split_samples(points):
    xy_samples = []
    y_buckets = split_point_buckets(points, Y_AXIS, 0.5)
    for ypoints in y_buckets:
        xy_samples.extend(split_point_buckets(ypoints, X_AXIS, 0.5))

    print("Found {} samples".format(len(xy_samples)))
    y_rows = len(y_buckets)
    x_rows = len(xy_samples)//y_rows

    return xy_samples, x_rows, y_rows


def cals_lows(xy_samples):
    xy_lows = []
    for i in range(len(xy_samples)):
        spoints = xy_samples[i]
        low = min(spoints, key=lambda p: p[Z_AXIS])
        xy_lows.insert(i, low)
    return xy_lows


def xcol(points):
    return [p[X_AXIS] for p in points]

def ycol(points):
    return [p[Y_AXIS] for p in points]

def zcol(points):
    return [p[Z_AXIS] for p in points]


x_arr = []
y_arr = []
z_arr = []

for t in mesh.triangles: # [:5000]:
    for p in t:
        x_arr.append(p[X_AXIS])
        y_arr.append(p[Y_AXIS])
        z_arr.append(p[Z_AXIS])

# Figure Origin

fig = plt.figure(figsize=(20, 10))
ax1 = plt.subplot(221, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.view_init(elev=45, azim=45)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='gray')

ax1 = plt.subplot(222, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.view_init(elev=0, azim=90)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='gray')

ax1 = plt.subplot(223, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.view_init(elev=0, azim=0)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='gray')

ax1 = plt.subplot(224, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.view_init(elev=90, azim=0)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='gray')

# plt.show()
# exit()


z_arr = [-z for z in z_arr]

move_zero(x_arr)
move_zero(y_arr)
move_zero(z_arr)
points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]


high_point = max(points, key=lambda p: p[Z_AXIS])
rotate_xy_rad(y_arr, z_arr, -atan(high_point[Z_AXIS]/high_point[Y_AXIS]))
points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]

high_point = max(points, key=lambda p: p[Z_AXIS])
rotate_xy_rad(x_arr, z_arr, -atan(high_point[Z_AXIS]/high_point[X_AXIS]))
points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]

mid_point = (0, 0, 0)
quadrant_points = [p for p in points if p[0] > 0 and p[1] > 0 and p[2] > 0]
corner_point = max(quadrant_points, key=lambda p: distance(mid_point, p))
rotate_xy_rad(x_arr, y_arr, atan(corner_point[Y_AXIS]/corner_point[X_AXIS]))

#z_arr = [-z for z in z_arr]
all_points = [[x_arr[i], y_arr[i], z_arr[i]] for i in range(len(x_arr))]

xy_samples, x_rows, y_rows = split_samples(all_points)
xy_lows = cals_lows(xy_samples)

x_angles = []
for i in range(x_rows):
    x_lows = xy_lows[i*4:(i+1)*4]
    arc = np.polyfit(xcol(x_lows), zcol(x_lows), 1)
    r = atan((np.polyval(arc, 10) - np.polyval(arc, 0))/10)
    print("X row [{}] angle: {:.2f}".format(i, r*180/pi))
    x_angles.append(r)


# y_angles = []
# for i in range(y_rows):
#     y_lows = xy_lows[i::4]
#     arc = np.polyfit(ycol(y_lows), zcol(y_lows), 1)
#     r = atan(np.polyval(arc, 1))
#     print("Y row [{}] angle: {:.2f}".format(i, r*180/pi))
#     y_angles.append(r)




# # ax1.scatter(xcol(edges), ycol(edges), zcol(edges), s=20, c='red')

# x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)
# x_lows, y_lows, z_lows = xcol(xy_lows), ycol(xy_lows), zcol(xy_lows)
# print("x_lows: {}".format(x_lows))
# print("y_lows: {}".format(y_lows))
# print("z_lows: {}".format(z_lows))
# ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='green')
# ax1.scatter(x_lows, y_lows, z_lows, s=20, c='red')

# plt.show()
# exit(0)


# rotate Y
#x_lows = [min(points, key=lambda p: p[Z_AXIS]) for points in xy_samples[:4]]
#arc = np.polyfit(xcol(x_lows), zcol(x_lows), 1)
#r = atan((np.polyval(arc, 10) - np.polyval(arc, 0))/10)
r = sum(x_angles)/len(x_angles)
rotate_points_xy_rad(all_points, X_AXIS, Z_AXIS, -r)


xy_samples, _, _ = split_samples(all_points)
xy_lows = cals_lows(xy_samples)
y_angles = []
for i in range(y_rows):
    y_lows = xy_lows[i::4]
    arc = np.polyfit(ycol(y_lows), zcol(y_lows), 1)
    r = atan((np.polyval(arc, 10) - np.polyval(arc, 0))/10)
    print("Y row [{}] angle: {:.2f}".format(i, r*180/pi))
    y_angles.append(r)

# rotate X
r = sum(y_angles)/len(y_angles)
rotate_points_xy_rad(all_points, Y_AXIS, Z_AXIS, -r)


z_low_num = 1000

z_mins = sorted(all_points, key=lambda p: p[Z_AXIS])
z_min = sum([z[Z_AXIS] for z in z_mins[:z_low_num]])/z_low_num
z_min_str = ['{:.3f}'.format(m[Z_AXIS]) for m in z_mins[:10]]
print("min: {:.3f} {}".format(z_min, z_min_str))
for p in all_points:
    p[Z_AXIS] -= z_min
x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)


xy_samples, _, _ = split_samples(all_points)

for i, spoints in enumerate(xy_samples):
    #z_arr = zcol(spoints)
    heights = sorted(zcol(spoints))
    # print(" {} .. {}".format(heights[:5], heights[-5:]))
    low = sum(heights[:100])/100
    high = sum(heights[-5:])/5
    h = '{} .. {}'.format(['{:+.3f}'.format(z) for z in heights[:5]], ['{:+.3f}'.format(z) for z in heights[-5:]])
    print("sample {:02d} thickness {:.3f}: {}".format(i+1, high-low, h))

# points = xy_samples[-4] + xy_samples[-3] + xy_samples[-2] + xy_samples[-1]
x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)


# Figure Rotated

fig = plt.figure(figsize=(20, 10))
ax1 = plt.subplot(111, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.view_init(elev=35, azim=15)
ax1.set_xlim(40, -40)
ax1.set_ylim(-40, 40)
ax1.set_zlim(-1, 5)

points = [p for p in all_points if p[Z_AXIS] >= 0]
x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='blue')

points = [p for p in all_points if p[Z_AXIS] < 0]
x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='cyan')


points = xy_samples[-4] + xy_samples[-3] + xy_samples[-2] + xy_samples[-1]
x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)

# # Figure 2

# fig = plt.figure(figsize=(20, 10))
# gs = fig.add_gridspec(ncols=2, nrows=2, wspace=0.5)

# ax2 = plt.subplot(gs[0,1])
# ax2.set_xlim(min(x_arr), max(x_arr))
# ax2.set_ylim(-0.5, 2.0)
# ax2.scatter(x_arr, z_arr, s=0.01, c='blue')
# ax2.scatter(xcol(x_lows), zcol(x_lows), s=20, c='red')
# ax2.minorticks_on()
# ax2.grid(which='major')
# ax2.grid(which='minor', linestyle=':')
# ax2.set_xlabel('x')
# ax2.set_ylabel('z')

# x = [-100, 100]
# ax2.add_line(mlines.Line2D(x, np.polyval(arc, x), lw=1, c='red'))
# #
# #ax2.grid(which='minor', alpha=0.2)
# #ax2.plot([-10, 10], [np.polyval(arc, -10), np.polyval(arc, 10)], '-')
# # plt.axline(arc, slope=0.25, color="red")

# ax3 = plt.subplot(gs[1,1])
# ax3.set_xlim(min(y_arr), max(y_arr))
# ax3.set_ylim(-0.5, 2.0)
# ax3.scatter(y_arr, z_arr, s=0.01, c='deepskyblue')
# ax3.scatter(ycol(y_lows), zcol(y_lows), s=20, c='red')
# ax3.yaxis.set_minor_locator(AutoMinorLocator(20))
# ax3.minorticks_on()
# ax3.grid(which='major')
# ax3.grid(which='minor', linestyle=':')
# ax3.set_xlabel('y')
# ax3.set_ylabel('z')

# Figure 3

fig = plt.figure(figsize=(20, 10))
gs = fig.add_gridspec(ncols=2*x_rows, nrows=y_rows, wspace=0.5, hspace=0.5)

def draw_samples(xy_samples, x_color=None, y_color=None):
    for i in range(x_rows):
        for j in range(y_rows):
            points = xy_samples[i + y_rows*j]
            low_points = [xy_lows[i + y_rows+j]]
            x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)

            ax_n = plt.subplot(gs[x_rows-i-1, j])
            ax_n.set_xlim(min(y_arr), max(y_arr))
            ax_n.set_ylim(-0.1, 1.5)
            ax_n.minorticks_on()
            ax_n.grid(which='major', lw=0.5, c='black')
            ax_n.grid(which='minor', alpha=0.5)
            ax_n.scatter(y_arr, z_arr, s=0.01, c=y_color or 'blue')
            ax_n.set_xlabel('y')
            ax_n.set_ylabel('z')

            ax_n.scatter(ycol(low_points), zcol(low_points), s=20, c='red')

            ax_n = plt.subplot(gs[j, x_rows+i])
            ax_n.set_xlim(min(x_arr), max(x_arr))
            ax_n.set_ylim(-0.1, 1.5)
            ax_n.minorticks_on()
            ax_n.grid(which='major', lw=0.5, c='black')
            ax_n.grid(which='minor', alpha=0.5)
            ax_n.scatter(x_arr, z_arr, s=0.01, c=x_color or 'deepskyblue')
            ax_n.set_xlabel('x')
            ax_n.set_ylabel('z')

            ax_n.scatter(xcol(low_points), zcol(low_points), s=20, c='red')

draw_samples(xy_samples)

# print("rotate a bit more")
# rotate_points_xy_rad(all_points, Y_AXIS, Z_AXIS, atan(0.1/35))

# xy_samples, _, _ = split_samples(all_points,)
# draw_samples(xy_samples, y_color='red', x_color='coral')

plt.show()
