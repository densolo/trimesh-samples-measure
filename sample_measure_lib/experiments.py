
from .calcs import *


def calc_x_angles_by_rows(xy_lows, x_rows, y_rows):
    x_angles = []
    for i in range(x_rows):
        x_lows = xy_lows[i*y_rows:(i+1)*y_rows]
        r = polyfit_line2rad(xcol(x_lows), zcol(x_lows))
        print("X row [{}] angle: {:.2f}".format(i, rad2deg(r)))
        x_angles.append(r)
    return x_angles


def calc_y_angles_by_rows(xy_lows, x_rows, y_rows):
    print("calc_y_angles_by_rows")
    y_angles = []
    for i in range(y_rows):
        y_lows = xy_lows[i::x_rows]
        r = polyfit_line2rad(ycol(y_lows), zcol(y_lows))
        print("Y row [{}] angle: {:.2f}".format(i, rad2deg(r)))
        y_angles.append(r)
    return y_angles


def calc_x_angles_by_corners(xy_samples, x_rows, y_rows):
    print("calc_x_angles_by_corners")
    i4 = x_rows * y_rows - 1
    i3 = i4 - x_rows + 1
    i2 = x_rows - 1
    i1 = 0

    x_angles = []
    sz = len(xy_samples[0])//2
    row1 = sorted(xy_samples[i1], key=lambda p: p[Z_AXIS])[-sz:] + sorted(xy_samples[i2], key=lambda p: p[Z_AXIS])[-sz:]

    r = polyfit_line2rad(xcol(row1), zcol(row1))
    print("  X row [{}] angle: {:.2f}".format(1, r*180/pi))
    x_angles.append(r)

    row1 = sorted(xy_samples[i3], key=lambda p: p[Z_AXIS])[-sz:] + sorted(xy_samples[i4], key=lambda p: p[Z_AXIS])[-sz:]
    
    r = polyfit_line2rad(xcol(row1), zcol(row1))    
    print("  X row [{}] angle: {:.2f}".format(2, r*180/pi))
    x_angles.append(r)

    return x_angles


def calc_y_angles_by_corners(xy_samples, x_rows, y_rows):
    print("calc_y_angles_by_corners")
    i4 = x_rows * y_rows - 1
    i3 = i4 - x_rows + 1
    i2 = x_rows - 1
    i1 = 0

    y_angles = []
    sz = len(xy_samples[0])//2
    row1 = sorted(xy_samples[i1], key=lambda p: p[Z_AXIS])[-sz:] + sorted(xy_samples[i3], key=lambda p: p[Z_AXIS])[-sz:]
    r = polyfit_line2rad(ycol(row1), zcol(row1))
    print("  Y row [{}] angle: {:.2f}".format(1, r*180/pi))
    y_angles.append(r)

    row1 = sorted(xy_samples[i2], key=lambda p: p[Z_AXIS])[-sz:] + sorted(xy_samples[i4], key=lambda p: p[Z_AXIS])[-sz:]
    r = polyfit_line2rad(ycol(row1), zcol(row1))
    print("  Y row [{}] angle: {:.2f}".format(2, r*180/pi))
    y_angles.append(r)

    return y_angles


def calc_xy_rad_by_corner(points):
    mid_point = (0, 0, 0)
    quadrant_points = [p for p in points if p[0] > 0 and p[1] > 0 and p[2] > 0]
    corner_point = max(quadrant_points, key=lambda p: distance_xy(mid_point, p))

    xy_r = deg2rad(45) - atan(corner_point[Y_AXIS]/corner_point[X_AXIS]) 
    print("Rotate XY: {}".format(xy_r * 180/pi))
    return xy_r


def adjust_zero_base(all_points):
    z_low_num = 1000

    z_mins = sorted(all_points, key=lambda p: p[Z_AXIS])
    z_min = sum([z[Z_AXIS] for z in z_mins[:z_low_num]])/z_low_num
    z_min_str = ['{:.3f}'.format(m[Z_AXIS]) for m in z_mins[:10]]
    print("Adjust base-level by min Z-value: {:.3f} {}".format(z_min, z_min_str))
    for p in all_points:
        p[Z_AXIS] -= z_min

