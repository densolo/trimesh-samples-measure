import lxml
import trimesh
import os
import sys
import time


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

import math
import scipy as sp
import scipy.interpolate
from scipy import spatial
import scipy.constants as consts

from scipy.ndimage import gaussian_filter
from skimage import filters
from skimage import feature
from skimage import measure
from skimage import segmentation
from skimage.morphology import square, dilation
from skimage.transform import probabilistic_hough_line


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
        measure_file_with_images(path, img_handler=ImageHandler(plt, path))
    

def measure_file_with_images(path, img_handler=None, start_id=None, gauss_sigma=None, canny_sigma=None):
    t0 = time.time()

    print("measure_file_with_images file: {} ID: {}".format(path, start_id))
    if img_handler is None:
        img_handler = ImageHandler(plt, path)

    points = load_points(path)
    x_arr, y_arr, z_arr = xyz_cols(points)

    img_handler.draw_points4_and_save(points, '3d-origin')

    points = zero_normalize_points(points)
    points = rotate_flat_z(points)
    points = rotate_points_xy_auto90(points)
    #points = rotate_points_xy_max_samples(points)
    #points = measure_file_with_images(points)    
    
    points = rotate_flat_z_micro(points)
    points = adjust_zero_base(points)

    xy_samples, x_rows, y_rows = split_samples(points)

    img_handler.draw_points4_and_save(points, '3d-rotated')

    points = rotate_each_sample(points)
    img_handler.draw_points4_and_save(points, '3d-rotated-xy')

    inter_points, xy_shape = scatter_to_grid_points(points)
    img, shape_points = filter_shape_edges(inter_points, xy_shape, gauss_sigma=gauss_sigma, canny_sigma=canny_sigma)
    
    # points = adjust_zero(inter_points, shape_points)    
    points = shape_points

    img_handler.draw_points4_and_save(points, '3d-inter')

    #inter_points, xy_shape = scatter_to_grid_points(points)
    #img_handler.draw_image_and_save(inter_points, xy_shape, 'photo')

    detect_lines(inter_points, xy_shape, plt)
    #inter_points, xy_shape = scatter_to_grid_points(points)
    #detect_lines(inter_points, xy_shape, plt)
    img_handler.save_image('photo')    

    xy_samples, x_rows, y_rows = split_samples(points)
    csv_path = print_thinkness_csv_id(xy_samples, x_rows, y_rows, start_id, path)
    img_handler.show_csv(csv_path)

    img_handler.draw_samples_and_save(xy_samples, None, x_rows, y_rows, '2d-matrix', start_id=start_id)


    dt = time.time() - t0
    print("Done in {:.1f} seconds".format(dt))


def validate_samples_or_fail(xy_samples, points, img_handler):
    pass
    # if len(xy_samples) < 4 or len(xy_samples) > 32:
    #     print("Unable to split on samples after rotation. Check the picture to adjust samples layout")
    #     img_handler.draw_points4_and_save(points, '3d-split-failure')        
    #     raise


def zero_normalize_points(points):
    print("zero_normalize_points")
    x_arr, y_arr, z_arr = xyz_cols(points)
    z_arr = [-z for z in z_arr]
    move_zero(x_arr, y_arr, z_arr)
    points = [(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(x_arr))]
    return points


def rotate_flat_z(points):
    print("rotate_flat_z")
    x_arr, y_arr, z_arr = xyz_cols(points)
    r = polyfit_line2rad(ycol(points), zcol(points))
    rotate_xy_rad(y_arr, z_arr, -r)
    points = col2points(x_arr, y_arr, z_arr)

    r = polyfit_line2rad(xcol(points), zcol(points))
    rotate_xy_rad(x_arr, z_arr, -r)
    points = col2points(x_arr, y_arr, z_arr)
    return points


def rotate_points_xy_auto90(points, plt=None):
    print("rotate_points_xy_auto90")
    inter_points, xy_shape = scatter_to_grid_points(points)
    img, lines = detect_lines(inter_points, xy_shape, plt=plt)
    xy_d = calc_rotate_angle_degree(lines)
    xy_r = deg2rad(xy_d)
    return rotate_points_xy(points, -xy_r)


def rotate_points_xy(points, xy_r):
    print("rotate_points_xy")
    x_arr, y_arr, z_arr = xyz_cols(points[:])
    rotate_xy_rad(x_arr, y_arr, xy_r)
    points = col2points(x_arr, y_arr, z_arr)
    return points


def rotate_points_xy_max_samples(points):
    print("rotate_points_xy_max_samples")
    max_samples = len(split_samples(points)[0])
    max_d = 0
    
    micro_angles = sorted(list(np.linspace(0.5,5.,5)) + list(np.linspace(-0.5,-5,5)), key=abs)
    for d in micro_angles:
        r_points = rotate_points_xy(points, deg2rad(d))
        xy_samples, _, _ = split_samples(r_points)
        if len(xy_samples) > max_samples:
            max_samples = len(xy_samples)
            max_d = d
                
    print("Found max samples {} at {} degree".format(max_samples, max_d))
    return rotate_points_xy(points, deg2rad(max_d))


def rotate_flat_z_micro(points):
    print("rotate_flat_z_micro")
    points = points[:]
    
    # rotate X/Z
    xy_samples, x_rows, y_rows = split_samples(points)
    xy_lows = calc_lows(xy_samples)
    x_angles = calc_x_angles_by_rows(xy_lows, x_rows, y_rows)
    #x_angles = calc_x_angles_by_corners(xy_samples, x_rows, y_rows)

    r = sum(x_angles)/len(x_angles)
    rotate_points_xy_rad(points, X_AXIS, Z_AXIS, -r)
    
    # rotate X/Z
    xy_samples, x_rows, y_rows = split_samples(points)
    y_angles = calc_y_angles_by_rows(xy_lows, x_rows, y_rows)
    #y_angles = calc_y_angles_by_corners(xy_samples, x_rows, y_rows)

    r = sum(y_angles)/len(y_angles)
    rotate_points_xy_rad(points, Y_AXIS, Z_AXIS, -r)
    return points


def scatter_to_grid_points(points):
    points = np.array(points)
    space_points = find_space_points(points, 0.5)
    grid_points, xy_shape = build_grid(points, 0.1)

    real_points = np.vstack([points, space_points])
    inter_points = interpolate_points(real_points, grid_points, xy_shape)
    return inter_points, xy_shape


def calc_rotate_angle_degree(lines):
    if not lines:
        return 0
        
    angles = []
    round_degrees = 5

    for line in lines:
        p0, p1 = line
        h = p1[1] - p0[1]
        w = p1[0] - p0[0]
        if w and h:
            r = atan(h/w)
            a = a0 = r/consts.degree
            
            if -90 < a < -45:
                a = 90 + a
            elif 45 < a < 90:
                a = a - 90
        else:
            a = a0 = 0

        print("angle: {:6.2f} => {:6.2f} ({})".format(a0, a, np.round(a/round_degrees)*round_degrees))
        angles.append(a)
    
    d = sum(angles)/len(angles)
    d1 = calc_avg_angle_v1(angles, round_degrees)

    print("Found angle: {:6.2f} ({:6.2f})".format(d, d1))
    return d


def calc_avg_angle_v1(angles, round_degrees):
    angles = np.unique(np.round(np.array(angles)/round_degrees)*round_degrees, return_counts=True)
    #print("calc_rotate_angle_degree angles: {}".format(angles))
    
    most_angles = sorted(np.array(angles).T, key=lambda it: it[1])
    for it in most_angles:
        print("{:6.2f}: {:3.0f}".format(it[0], it[1]))
    
    most_angles = most_angles[-2:]
    if not most_angles:
        print("Unable to determine rotation angle from {}".format(angles))
        return 0
    
    d = sorted(most_angles, key=lambda it: it[0])[0][0]
    print("angles: {}".format(angles))
    angles = [a for a in angles[0] if abs(a - d) < round_degrees/2]
    return sum(angles)/len(angles)


def interpolate_points(real_points, grid_points, xy_shape):
   
    print("interpolate_points begin real: {} grid: {}".format(real_points.size, grid_points.size))

    xy_real = real_points[:,:2]
    x_real = real_points[:,2]
    interp = sp.interpolate.LinearNDInterpolator(xy_real, x_real, fill_value=0)
    # interp = sp.interpolate.NearestNDInterpolator(xy_real, x_real)
    # interp = sp.interpolate.Rbf(bx,by,x_real,smooth=1, episilon=1)
    
    B1 = grid_points[:,0].reshape(xy_shape[0], xy_shape[1])
    B2 = grid_points[:,1].reshape(xy_shape[0], xy_shape[1])
    Z = interp(B1,B2)

    print("interpolate_points completed")
    return np.vstack([B1.ravel(),B2.ravel(),Z.ravel()]).T


def detect_lines(points, xy_shape, plt=None):
    img = points[:,2].reshape(xy_shape[1], xy_shape[0])
    img2 = gaussian_filter(img, sigma=4)
    img4 = feature.canny(img2, sigma=5)
    img4 = np.where(img4, 1.0, 0)
    img6 = segmentation.flood_fill(img4, (1, 1), 1.0, connectivity=1)
    
    print("detect_lines in {}".format(img.shape))
    lines = probabilistic_hough_line(img4, threshold=5, line_length=60, line_gap=20)
    print("found {} lines".format(len(lines)))
    
    if plt:
        fig = plt.figure(figsize=(20, 10))
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        ax1.imshow(img, cmap=plt.cm.gray)
        ax2.imshow(img4, cmap=plt.cm.gray)

        for line in lines:
            p0, p1 = line
            ax2.plot((p0[0], p1[0]), (p0[1], p1[1]), c='r')

    return img6, lines


def filter_shape_edges(points, xy_shape, plt=None, gauss_sigma=None, canny_sigma=None):
    img = points[:,2].reshape(xy_shape[1], xy_shape[0])
    img2 = gaussian_filter(img, sigma=gauss_sigma or 4)
    img4 = feature.canny(img2, sigma=canny_sigma or 5)
    img4a = np.where(img4, 1.0, 0.)
    
    s = square(10)
    s[:,:] = 0
    s[:,2] = 1
    s[2,:] = 1

    img4 = dilation(img4a, s)
    img4b = dilation(img4a, square(5))

    img6 = segmentation.flood_fill(img4, (1, 1), 1.0, connectivity=1)    
    i = img6.ravel() == 0
    shape_points = points[i]
    
    img7 = np.where(img6, 0, img)
    
    # debug begin
    if plt:
        fig = plt.figure(figsize=(20, 20))
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)
        
        ax1.imshow(img, cmap=plt.cm.gray)
        ax2.imshow(img7, cmap=plt.cm.gray)
        ax3.imshow(img4, cmap=plt.cm.gray)
        ax4.imshow(img4b, cmap=plt.cm.gray)
        
    # debug end
    
    return img, shape_points


def calc_frame(points, margin=1):
    points = np.array(points)
   
    xmin = np.min(points[:,0])
    xmax = np.max(points[:,0])
    ymin = np.min(points[:,1])
    ymax = np.max(points[:,1])
    
    xmin = math.floor(xmin - margin)
    xmax = math.ceil(xmax + margin)
    
    ymin = math.floor(ymin - margin)
    ymax = math.ceil(ymax + margin)
    
    return [(xmin, ymin), (xmax,ymax)]


def build_grid(points, grid_step, z_val=0):
    points = np.array(points)
   
    corners = calc_frame(points)
    x_lim = corners[0][0], corners[1][0]
    y_lim = corners[0][1], corners[1][1]
    
    xy_shape = (
            int(abs(x_lim[1]-x_lim[0])/grid_step),
            int(abs(y_lim[1]-y_lim[0])/grid_step)
        )
    
    print("generate grid {}x{} with z: {:.3f} step: {}".format(xy_shape[0], xy_shape[1], z_val, grid_step))
    
    x_grid = np.linspace(x_lim[0], x_lim[1], xy_shape[0])
    y_grid = np.linspace(y_lim[0], y_lim[1], xy_shape[1])

    B1, B2 = np.meshgrid(x_grid, y_grid, indexing='xy')
    Z = np.ones(len(B1.ravel())) * z_val

    return np.vstack([B1.ravel(),B2.ravel(),Z.ravel()]).T, xy_shape


def find_space_points(points, grid_step=0.5):
    points = np.array(points)
    
    z_base = np.min(points[:,2])
    grid_points, xy_shape = build_grid(points, grid_step, z_base)
    
    real_points_tree = spatial.KDTree(points[:,:2])
    indexes = real_points_tree.query(grid_points[:,:2], distance_upper_bound=grid_step)
    indexes = np.isinf(indexes[0])
    return grid_points[indexes]


def adjust_zero(inter_points, shape_points):
    heights = sorted(zcol(inter_points))
    low = sum(heights[:100])/100
    print("adjust_zero by {}".format(low))

    b = np.transpose(shape_points)
    shape_points = np.transpose(np.vstack([b[:2,:], b[2,:] - low]))
    #inter_points = np.array(list(filter(lambda p: p[2] > 0.1, inter_points)))
    return shape_points


def rotate_each_sample(points, img_handler=None):
    xy_samples, _, _ = split_samples(points)
    new_points = []
    for i, s in enumerate(xy_samples):
        print("--- {} ---".format(i+1))
        s = rotate_sample(s, i, img_handler)
        new_points.extend(s)
    return new_points


def rotate_sample(s, i=None, img_handler=None): 
    #xy_r = deg2rad(6)
    #s = rotate_points_xy(s, -xy_r)

    x_arr, y_arr, z_arr = xyz_cols(s)

    x_mid = sum(find_limit(x_arr))/2
    y_mid = sum(find_limit(y_arr))/2

    x_arr[:] = [x - x_mid for x in x_arr]
    y_arr[:] = [y - y_mid for y in y_arr]
    s = col2points(x_arr, y_arr, z_arr)

    if img_handler:
        s = rotate_points_xy_auto90(s, plt)
        img_handler.save_image("photo-{}".format(i))
    else:
        s = rotate_points_xy_auto90(s)
    
    x_arr, y_arr, z_arr = xyz_cols(s)
    x_arr[:] = [x + x_mid for x in x_arr]
    y_arr[:] = [y + y_mid for y in y_arr]
    s = col2points(x_arr, y_arr, z_arr)

    #inter_points, xy_shape = scatter_to_grid_points(s)
    #img, lines = detect_lines(inter_points, xy_shape)

    #rotate_sample(s)
    # draw_samples_ex(plt, [s], None, 1, 1)
    return s


if __name__ == '__main__':
    main()
