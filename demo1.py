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

xy_samples = []
y_buckets = split_point_buckets(all_points, Y_AXIS, 0.5)
for ypoints in y_buckets:
    xy_samples.extend(split_point_buckets(ypoints, X_AXIS, 0.5))
print("Found {} samples".format(len(xy_samples)))
rows = int(sqrt(len(xy_samples)))
y_rows = len(y_buckets)
x_rows = len(xy_samples)//y_rows

for i in range(rows):
    x_samples = xy_samples[i*4:(i+1)*4]
    #edges = x_samples
    x_lows = [min(points, key=lambda p: p[Z_AXIS]) for points in x_samples]
    edges = x_lows
    arc = np.polyfit(xcol(x_lows), zcol(x_lows), 1)
    r = atan(np.polyval(arc, 1))
    print("{} row angle: {} ({})".format(i, r*180/pi, arc))

# rotate Y
x_lows = [min(points, key=lambda p: p[Z_AXIS]) for points in xy_samples[:4]]
arc = np.polyfit(xcol(x_lows), zcol(x_lows), 1)
r = atan((np.polyval(arc, 10) - np.polyval(arc, 0))/10)
rotate_points_xy_rad(all_points, X_AXIS, Z_AXIS, -r)

# rotate X
y_lows = [min(points, key=lambda p: p[Z_AXIS]) for points in xy_samples[::4]]
y_arc = np.polyfit(ycol(y_lows), zcol(y_lows), 1)
y_r = atan((np.polyval(y_arc, 10) - np.polyval(y_arc, 0))/10)
rotate_points_xy_rad(all_points, Y_AXIS, Z_AXIS, -y_r)

z_low_num = 1000

z_mins = sorted(all_points, key=lambda p: p[Z_AXIS])
z_min = sum([z[Z_AXIS] for z in z_mins[:z_low_num]])/z_low_num
z_min_str = ['{:.3f}'.format(m[Z_AXIS]) for m in z_mins[:10]]
print("min: {:.3f} {}".format(z_min, z_min_str))
for p in all_points:
    p[Z_AXIS] -= z_min
x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)


xy_samples = []
y_buckets = split_point_buckets(all_points, Y_AXIS, 0.5)
for ypoints in y_buckets:
    xy_samples.extend(split_point_buckets(ypoints, X_AXIS, 0.5))

for i, spoints in enumerate(xy_samples):
    #z_arr = zcol(spoints)
    heights = sorted(zcol(spoints))
    # print(" {} .. {}".format(heights[:5], heights[-5:]))
    low = sum(heights[:100])/100
    high = sum(heights[-5:])/5
    h = '{} .. {}'.format(['{:.3f}'.format(z) for z in heights[:5]], ['{:.3f}'.format(z) for z in heights[-5:]])
    print("detail {:02d} height {:.3f}: {}".format(i+1, high-low, h))

# points = xy_samples[-4] + xy_samples[-3] + xy_samples[-2] + xy_samples[-1]
x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)


fig = plt.figure(figsize=(20, 10))
ax1 = plt.subplot(111, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.view_init(elev=35, azim=15)
ax1.set_xlim(40, -40)
ax1.set_ylim(-40, 40)
ax1.set_zlim(-1, 5)
#ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='grey')
ax1.scatter(xcol(edges), ycol(edges), zcol(edges), s=20, c='red')

points = [p for p in all_points if p[Z_AXIS] >= 0]
x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='blue')

points = [p for p in all_points if p[Z_AXIS] < 0]
x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)
ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='cyan')


points = xy_samples[-4] + xy_samples[-3] + xy_samples[-2] + xy_samples[-1]
x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)

fig = plt.figure(figsize=(20, 10))
gs = fig.add_gridspec(ncols=2, nrows=2, wspace=0.5)

ax2 = plt.subplot(gs[0,1])
ax2.set_xlim(min(x_arr), max(x_arr))
ax2.set_ylim(-0.5, 2.0)
ax2.scatter(x_arr, z_arr, s=0.01, c='blue')
ax2.scatter(xcol(x_lows), zcol(x_lows), s=20, c='red')
ax2.minorticks_on()
ax2.grid(which='major')
ax2.grid(which='minor', linestyle=':')
ax2.set_xlabel('x')
ax2.set_ylabel('z')

x = [-100, 100]
ax2.add_line(mlines.Line2D(x, np.polyval(arc, x), lw=1, c='red'))
#
#ax2.grid(which='minor', alpha=0.2)
#ax2.plot([-10, 10], [np.polyval(arc, -10), np.polyval(arc, 10)], '-')
# plt.axline(arc, slope=0.25, color="red")

ax3 = plt.subplot(gs[1,1])
ax3.set_xlim(min(y_arr), max(y_arr))
ax3.set_ylim(-0.5, 2.0)
ax3.scatter(y_arr, z_arr, s=0.01, c='deepskyblue')
ax3.scatter(ycol(y_lows), zcol(y_lows), s=20, c='red')
ax3.yaxis.set_minor_locator(AutoMinorLocator(20))
ax3.minorticks_on()
ax3.grid(which='major')
ax3.grid(which='minor', linestyle=':')
ax3.set_xlabel('y')
ax3.set_ylabel('z')

#plt.show()


fig = plt.figure(figsize=(20, 10))
gs = fig.add_gridspec(ncols=2*x_rows, nrows=y_rows, wspace=0.5)

for i in range(x_rows):
    for j in range(y_rows):
        points = xy_samples[i + y_rows*j]
        x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)

        ax_n = plt.subplot(gs[j, i])
        ax_n.set_xlim(min(x_arr), max(x_arr))
        ax_n.set_ylim(-0.5, 2.0)
        ax_n.minorticks_on()
        ax_n.grid(which='major', lw=0.5, c='black')
        ax_n.grid(which='minor', alpha=0.5)
        ax_n.scatter(x_arr, z_arr, s=0.01, c='blue')
        ax_n.set_xlabel('x')
        ax_n.set_ylabel('z')

        ax_n = plt.subplot(gs[i, x_rows+j])
        ax_n.set_xlim(min(y_arr), max(y_arr))
        ax_n.set_ylim(-0.5, 2.0)
        ax_n.minorticks_on()
        ax_n.grid(which='major', lw=0.5, c='black')
        ax_n.grid(which='minor', alpha=0.5)
        ax_n.scatter(y_arr, z_arr, s=0.01, c='deepskyblue')
        ax_n.set_xlabel('y')
        ax_n.set_ylabel('z')

# ax2 = plt.subplot(222, projection='3d')
# ax2.view_init(elev=0, azim=0)
# ax2.set_xlim(-40, 40)
# ax2.set_ylim(-40, 40)
# ax2.set_zlim(0, 40)
# ax2.scatter(x_arr, y_arr, z_arr, s=0.01, c='grey')

# ax3 = plt.subplot(223, projection='3d')
# ax3.view_init(elev=20, azim=30)
# ax3.set_xlim(-40, 40)
# ax3.set_ylim(-40, 40)
# ax3.set_zlim(0, 40)
# ax3.scatter(x_arr, y_arr, z_arr, s=0.01, c='grey')

plt.show()

#move_zero(x_arr)
# move_zero(y_arr)
# move_zero(z_arr)

# # rotate_xy(x_arr, y_arr, 45)

# #verts = mesh.triangles[:10]
# #print(verts)
# ax1.set_xlabel('X')
# ax1.set_ylabel('Y')
# ax1.set_zlabel('Z')

# # ax2.view_init(elev=5, azim=5)
# # ax2.set_xlabel('X')
# # ax2.set_ylabel('Y')
# # ax2.set_zlabel('Z')

# # ax2.set_xlim(0,x_lim[1])
# # ax2.set_ylim(0,y_lim[1])
# # ax2.set_zlim(0,z_lim[1])

# # ax1.scatter(x_arr, y_arr, z_arr, s=0.1, c='blue')

# iz_lim = find_limit_indexes(z_arr)
# i = iz_lim[1]
# x_dots = [x_arr[i], 0]
# y_dots = [y_arr[i], 0]
# z_dots = [z_arr[i], 0]

# ax1.scatter(x_dots, y_dots, z_dots, s=10, c='blue')

# r = -atan(z_arr[i]/y_arr[i])
# print("r1: {} {}".format(y_dots, z_dots))
# rotate_xy_rad(y_dots, z_dots, r)
# print("r2: {} {}".format(y_dots, z_dots))
# ax1.scatter(x_dots, y_dots, z_dots, s=10, c='blue')
# rotate_xy_rad(y_arr, z_arr, r)
# #rotate_xy(x_arr, y_arr, 45)

# #

# iz_lim = find_limit_indexes(z_arr)
# i = iz_lim[1]
# x_dots = [x_arr[i]]
# y_dots = [y_arr[i]]
# z_dots = [z_arr[i]]

# # ax1.scatter(x_dots, y_dots, z_dots, s=10, c='green')

# r = -atan(z_arr[i]/x_arr[i])
# rotate_xy_rad(x_dots, z_dots, r)
# # ax1.scatter(x_dots, y_dots, z_dots, s=10, c='green')
# rotate_xy_rad(x_arr, z_arr, r)
# # rotate_xy(x_arr, y_arr, 45)

# #ax1.scatter(x_arr, y_arr, z_arr, s=0.1, c='blue')

# # rotate_xy(x_arr, y_arr, 22)

# # move_zero(x_arr)
# # move_zero(y_arr)
# # move_zero(z_arr)


# # rotate_xy(y_arr, z_arr, -atan(6/70)*180/pi)

# x_lim = find_limit(x_arr)
# y_lim = find_limit(y_arr)
# z_lim = find_limit(z_arr)
# yz_lim = max(y_lim[1], z_lim[1])

# ax1.view_init(elev=10, azim=40)
# ax1.set_xlim(*x_lim)
# ax1.set_ylim(*y_lim)
# ax1.set_zlim(0, 40)

# #ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='yellow')
# rotate_xy(x_arr, y_arr, 24)
# rotate_xy(x_arr, z_arr, 180)

# z_lim = find_limit(z_arr)
# print("height: {}".format(z_lim))

# ax1.scatter([0], [10], [0], s=10, c='red')

