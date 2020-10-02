import lxml
import trimesh
import os
import sys


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
from sample_measure_lib.draws_io import ImageHandler, ImageHandlerNull
from sample_measure_lib.formats import *
from sample_measure_lib.experiments import *
from sample_measure_lib.tsm_main_v3 import measure_file_with_images as measure_file_with_images_v3


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
        measure_file_with_images_v3(path, img_handler=ImageHandler(plt, path), start_id='A1', gauss_sigma=2, canny_sigma=3)

def measure_file_with_images(path, img_handler=None, start_id=None, gauss_sigma=None, canny_sigma=None):

    if img_handler is None:
        img_handler = ImageHandler(plt, path)

    points = load_points(path)
    x_arr, y_arr, z_arr = xyz_cols(points)

    img_handler.draw_points4_and_save(points, '3d-origin')

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
    validate_samples_or_fail(xy_samples, all_points, img_handler)

    # fine tune vertically to make flat

    # rotate Y/Z
    xy_lows = calc_lows(xy_samples)
    x_angles = calc_x_angles_by_rows(xy_lows, x_rows, y_rows)
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
    all_points = adjust_zero_base(all_points)
    x_arr, y_arr, z_arr = xyz_cols(all_points)

    xy_samples, _, _ = split_samples(all_points)
    validate_samples_or_fail(xy_samples, all_points, img_handler)


    print_thinkness_csv(xy_samples, path)

    x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)
    img_handler.draw_points4_and_save(all_points, '3d-rotated')


    #points = xy_samples[-4] + xy_samples[-3] + xy_samples[-2] + xy_samples[-1]
    #x_arr, y_arr, z_arr = xyz_cols(points)


    # Figure 3
    img_handler.draw_samples_and_save(xy_samples, xy_lows, x_rows, y_rows, '2d-matrix')

    # plt.show()
    print("Done")


def validate_samples_or_fail(xy_samples, points, img_handler):
    if len(xy_samples) < 4 or len(xy_samples) > 32:
        print("Unable to split on samples after rotation. Check the picture to adjust samples layout")
        img_handler.draw_points4_and_save(points, '3d-split-failure')        
        raise


if __name__ == '__main__':
    main()
