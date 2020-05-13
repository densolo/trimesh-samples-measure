import lxml
import trimesh
import os

path = os.path.join(os.path.dirname(__file__), "File.3mf")
#path = os.path.join(os.path.dirname(__file__), "data/Corner discs 1.3mf")
#path = os.path.join(os.path.dirname(__file__), "data/Corner Coins2.3mf")
#path = os.path.join(os.path.dirname(__file__), "data/Corner Coins 2 smoothed.3mf")

# assert os.path.exists(path)
# mesh = trimesh.load_mesh(path)

import numpy as np
from math import sin, cos, atan, pi, sqrt, pow

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.lines as mlines
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import matplotlib.gridspec as gridspec

from sample_measure_lib.calcs import *
from sample_measure_lib.draws import *
from sample_measure_lib.formats import *
from sample_measure_lib.experiments import *


points = load_points(path)
x_arr, y_arr, z_arr = xyz_cols(points)


# Figure Origin



# plt.show()
# exit()


z_arr = [-z for z in z_arr]

move_zero(x_arr, y_arr, z_arr)
points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]


r = polyfit_line2rad(ycol(points), zcol(points))
rotate_xy_rad(y_arr, z_arr, -r)


points = col2points(x_arr, y_arr, z_arr)


r = polyfit_line2rad(xcol(points), zcol(points))
rotate_xy_rad(x_arr, z_arr, -r)
points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]

# ax1 = draw_points(plt, points)
# plt.show()
# exit()

# high_point = max(points, key=lambda p: p[Z_AXIS])
# rotate_xy_rad(x_arr, z_arr, -atan(high_point[Z_AXIS]/high_point[X_AXIS]))
#points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]

# show_points(points)

# mid_point = (0, 0, 0)
# quadrant_points = [p for p in points if p[0] > 0 and p[1] > 0 and p[2] > 0]
# corner_point = max(quadrant_points, key=lambda p: distance_xy(mid_point, p))

# xy_r = deg2rad(45) - atan(corner_point[Y_AXIS]/corner_point[X_AXIS]) 
# print("r: {}".format(xy_r * 180/pi))

# ax1 = draw_points(plt, points)
# ax1.scatter(xcol([corner_point]), ycol([corner_point]), zcol([corner_point]), s=20, c='red')
# plt.show()
# exit()

xy_r = calc_xy_rad_by_corner(points)
rotate_xy_rad(x_arr, y_arr, xy_r)
all_points = col2points(x_arr, y_arr, z_arr)


xy_samples, x_rows, y_rows = split_samples(all_points)


xy_lows = calc_lows(xy_samples)
# x_angles = cacl_x_angles_by_rows(xy_lows, x_rows, y_rows)
x_angles = calc_x_angles_by_corners(xy_samples, x_rows, y_rows)


# rotate Y
r = sum(x_angles)/len(x_angles)
rotate_points_xy_rad(all_points, X_AXIS, Z_AXIS, -r)


xy_samples, _, _ = split_samples(all_points)
#y_angles = calc_y_angles_by_rows(xy_lows, x_rows, y_rows)
y_angles = calc_y_angles_by_corners(xy_samples, x_rows, y_rows)


# rotate X
r = sum(y_angles)/len(y_angles)
rotate_points_xy_rad(all_points, Y_AXIS, Z_AXIS, -r)


adjust_zero_base(all_points)
x_arr, y_arr, z_arr = xyz_cols(all_points)


xy_samples, _, _ = split_samples(all_points)
print_thinkness_csv(xy_samples)


x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)


draw_points4(plt, all_points)


points = xy_samples[-4] + xy_samples[-3] + xy_samples[-2] + xy_samples[-1]
x_arr, y_arr, z_arr = xyz_cols(points)


# Figure 3

draw_samples(plt, xy_samples, xy_lows, x_rows, y_rows)

plt.show()
