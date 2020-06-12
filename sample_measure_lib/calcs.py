
import os
import numpy as np
from math import sin, cos, atan, pi, sqrt, pow
import lxml
import trimesh

X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2

AXIS_NAMES = ['X', 'Y', 'X'] 


def load_points(path, size=None):
    print("Reading 3mf file {}".format(path))
    assert os.path.exists(path)
    mesh = trimesh.load_mesh(path)

    points = []

    triangles = mesh.triangles
    if size:
        triangles = triangles[:size]

    for t in triangles:
        for p in t:
            points.append([p[X_AXIS], p[Y_AXIS], p[Z_AXIS]])

    print("Loaded {} 3d points".format(len(points)))
    return points


def polyfit_line2rad(x_arr, y_arr):
    arc = np.polyfit(x_arr, y_arr, 1)
    return atan((np.polyval(arc, 100) - np.polyval(arc, 0))/100)


def rad2deg(r):
    return r*180/pi


def deg2rad(d):
    return d*pi/180


def rotate_xy(x_arr, y_arr, degree):
    return rotate_xy_rad(x_arr, y_arr, degree * pi / 180)


def rotate_xy_rad(x_arr, y_arr, r):
    print("Rotate: {:.2f} degree".format(r*180/pi))

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
    print("Rotate {}{}: {} degree".format(AXIS_NAMES[dim1], AXIS_NAMES[dim2], r*180/pi))

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


def move_zero(*arr):
    for x_arr in arr:
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


def distance_xy(p1, p2):
    return sqrt(sum([pow(p2[i] - p1[i], 2) for i in range(2)]))


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

    xy_samples = [s for s in xy_samples if len(s) > 1000]
    print("Found {} samples".format(len(xy_samples)))
    y_rows = len(y_buckets)
    x_rows = len(xy_samples)//y_rows

    return xy_samples, x_rows, y_rows


def calc_lows(xy_samples):
    xy_lows = []
    for i in range(len(xy_samples)):
        spoints = xy_samples[i]
        low = min(spoints, key=lambda p: p[Z_AXIS])
        xy_lows.insert(i, low)
    return xy_lows


def calc_high_avg(points, n1, n2):
     points = sorted(points, key=lambda p: p[Z_AXIS])
     lasts = points[-n1:-n2]
     values = [p[Z_AXIS] for p in  lasts]
     return sum(values)/len(values)


def xcol(points):
    return [p[X_AXIS] for p in points]

def ycol(points):
    return [p[Y_AXIS] for p in points]

def zcol(points):
    return [p[Z_AXIS] for p in points]

def xyz_cols(points):
    return xcol(points), ycol(points), zcol(points)

def col2points(x_arr, y_arr, z_arr):
    return [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]
