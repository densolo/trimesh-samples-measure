import lxml
import trimesh
import os
import sys


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


def usage():
    print("""
python tsm.py <file.3mf>
""")

def main():
    args = sys.argv[1:]
    if not args or args[0] in ('help', '-h'):
        usage()
        exit()

    for path in args:
        measure_file_with_images(path)
    
def measure_file_with_images(path):
    points = load_points(path)
    x_arr, y_arr, z_arr = xyz_cols(points)

    draw_points4(plt, points)
    save_image(path, '3d-origin')

    # reverse upside down
    z_arr = [-z for z in z_arr]
    move_zero(x_arr, y_arr, z_arr)
    points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]


    # rotate vertically for x and y to make flat
    r = polyfit_line2rad(ycol(points), zcol(points))
    rotate_xy_rad(y_arr, z_arr, -r)

    points = col2points(x_arr, y_arr, z_arr)
    r = polyfit_line2rad(xcol(points), zcol(points))
    rotate_xy_rad(x_arr, z_arr, -r)
    points = col2points(x_arr, y_arr, z_arr)

    # rotate horizontally to parallel with x and y axis
    xy_r = calc_xy_rad_by_corner(points)
    rotate_xy_rad(x_arr, y_arr, xy_r)
    all_points = col2points(x_arr, y_arr, z_arr)


    # split samples
    xy_samples, x_rows, y_rows = split_samples(all_points)
    validate_samples_or_fail(xy_samples, all_points)

    # fine tune vertically to make flat

    # rotate Y/Z
    xy_lows = calc_lows(xy_samples)
    x_angles = cacl_x_angles_by_rows(xy_lows, x_rows, y_rows)
    #x_angles = calc_x_angles_by_corners(xy_samples, x_rows, y_rows)

    r = sum(x_angles)/len(x_angles)
    rotate_points_xy_rad(all_points, X_AXIS, Z_AXIS, -r)

    # rotate X/Z
    xy_samples, _, _ = split_samples(all_points)
    y_angles = calc_y_angles_by_rows(xy_lows, x_rows, y_rows)
    #y_angles = calc_y_angles_by_corners(xy_samples, x_rows, y_rows)

    r = sum(y_angles)/len(y_angles)
    rotate_points_xy_rad(all_points, Y_AXIS, Z_AXIS, -r)

    # move up-down to baseline along Z
    adjust_zero_base(all_points)
    x_arr, y_arr, z_arr = xyz_cols(all_points)

    xy_samples, _, _ = split_samples(all_points)
    validate_samples_or_fail(xy_samples, all_points)


    print_thinkness_csv(xy_samples, path)

    x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)
    draw_points4(plt, all_points)
    save_image(path, '3d-rotated')


    points = xy_samples[-4] + xy_samples[-3] + xy_samples[-2] + xy_samples[-1]
    x_arr, y_arr, z_arr = xyz_cols(points)


    # Figure 3
    draw_samples(plt, xy_samples, xy_lows, x_rows, y_rows)
    save_image(path, '2d-matrix')

    # plt.show()
    print("Done")


def validate_samples_or_fail(xy_samples, points):
    if len(xy_samples) < 4 or len(xy_samples) > 32:
        print("Unable to split on samples after rotation. Check the picture to adjust samples layout")
        draw_points4(plt, points)
        save_image(path, '3d-split-failure')
        raise


if __name__ == '__main__':
    main()
