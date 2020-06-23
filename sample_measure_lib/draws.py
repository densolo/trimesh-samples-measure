import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.lines as mlines
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D

from .calcs import *
from .formats import *


def draw_points(plt, all_points):
    x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)

    plt.figure(figsize=(20, 10))
    ax1 = plt.subplot(111, projection='3d')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.view_init(elev=45, azim=45)
    ax1.scatter(x_arr, y_arr, z_arr, s=0.01, c='gray')
    return ax1


def draw_points4(plt, all_points):
    x_arr, y_arr, z_arr = xcol(all_points), ycol(all_points), zcol(all_points)

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

    return fig


def save_image(path, suffix):
    outpath = build_output_file(path, suffix, 'png')
    print("Saving image into {}".format(outpath))
    plt.savefig(outpath)


def draw_samples(plt, xy_samples, xy_lows, x_rows, y_rows, x_color=None, y_color=None):
    ylim = [-0.1, 2]

    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(ncols=2*x_rows, nrows=y_rows, wspace=0.5, hspace=0.5)

    for i in range(x_rows):
        for j in range(y_rows):
            k = i + y_rows*j
            points = xy_samples[k]
            #low_points = [xy_lows[i + y_rows+j]]
            x_arr, y_arr, z_arr = xcol(points), ycol(points), zcol(points)

            #ax_n = plt.subplot(gs[x_rows-i-1, j])
            ax_n = plt.subplot(gs[j, i])
            ax_n.set_xlim(min(y_arr), max(y_arr))
            ax_n.set_ylim(*ylim)
            ax_n.minorticks_on()
            ax_n.grid(which='major', lw=0.5, c='black')
            ax_n.grid(which='minor', alpha=0.5)
            ax_n.scatter(y_arr, z_arr, s=0.01, c=y_color or 'blue')
            ax_n.set_xlabel('y ({})'.format(k+1))
            ax_n.set_ylabel('z')

            # ax_n.scatter(ycol(low_points), zcol(low_points), s=20, c='red')

            # ax_n = plt.subplot(gs[j, x_rows+i])
            # ax_n.set_xlim(min(x_arr), max(x_arr))
            # ax_n.set_ylim(*ylim)
            # ax_n.minorticks_on()
            # ax_n.grid(which='major', lw=0.5, c='black')
            # ax_n.grid(which='minor', alpha=0.5)
            # ax_n.scatter(x_arr, z_arr, s=0.01, c=x_color or 'deepskyblue')
            # ax_n.set_xlabel('x ({})'.format(k+1))
            # ax_n.set_ylabel('z')

            ax_n = plt.subplot(gs[j, x_rows+i])
            ax_n.set_xlim(min(x_arr), max(x_arr))
            ax_n.set_ylim(max(y_arr), min(y_arr))
            ax_n.minorticks_on()
            ax_n.grid(which='major', lw=0.5, c='black')
            ax_n.grid(which='minor', alpha=0.5)
            ax_n.scatter(x_arr, y_arr, s=0.01, c=x_color or 'green')
            ax_n.set_xlabel('x ({})'.format(k+1))
            ax_n.set_ylabel('y')

            # ax_n.scatter(xcol(low_points), zcol(low_points), s=20, c='red')
