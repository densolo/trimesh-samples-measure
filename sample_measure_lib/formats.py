
import os
import re

from .calcs import *
import numpy as np


def fmt3f(f):
    return "{:.3f}".format(f)


def fmt63f(f):
    return "{:+07.3f}".format(f)


def fmt0f(f):
    return "{:.0f}".format(f)


def fmt20f(f):
    return "{:+03.0f}".format(f)


def generate_thinkness_csv(xy_samples):
    lines = []
    lines.append([
        "SAMPLE",
        "MAX",
        "X",
        "Y" 
    ])
    for i, spoints in enumerate(xy_samples):
        heights = sorted(zcol(spoints))
        # print(" {} .. {}".format(heights[:5], heights[-5:]))
        low = sum(heights[:100])/100
        high = sum(heights[-50:-10])/40
        #h = '{} .. {}'.format(['{:+.3f}'.format(z) for z in heights[:5]], ['{:+.3f}'.format(z) for z in heights[-5:]])
        #print("sample {:02d} thickness {:.3f}: x:{:+3.0f} y:{:+3.0f}".format(i+1, high-low, spoints[0][0], spoints[0][1]))
        lines.append([
            "{:02}".format(i+1),
            "{:.3f}".format(high-low), 
            "{:+03.0f}".format(spoints[0][X_AXIS]),
            "{:+03.0f}".format(spoints[0][Y_AXIS])
        ])
    return lines


def validate_start_id(start_id):
    if not start_id:
        start_id = 'A1'
    
    if not re.match('^[A-Z][0-9]$', start_id):
        raise Exception("ID must be [A-Z][0-9] e.g. A1 or E1")


def format_sample_id(x, y, start_id):
    start_id = start_id or 'A1'
    
    x_start = start_id[0]
    y_start = int(start_id[1])
    s_id = "{}{}".format(chr(ord(x_start) + x), y_start + y)
    return s_id.upper()


def generate_thinkness_csv_id(xy_samples, x_rows, y_rows, start_id, calc_low=False):
    lines = []
    lines.append([
        "ID",
        "Z",
        "X",
        "Y",
        "AVG",
        "SD"
    ])

    validate_start_id(start_id)
    
    for j in range(y_rows):
        for i in range(x_rows):
            k = i + j*x_rows
            spoints = xy_samples[k]
            s_id = format_sample_id(i, j, start_id)

            heights = sorted(zcol(spoints))
            # print(" {} .. {}".format(heights[:5], heights[-5:]))
            low = sum(heights[:100])/100 if calc_low else 0
            high = sum(heights[-50:-10])/40
            #h = '{} .. {}'.format(['{:+.3f}'.format(z) for z in heights[:5]], ['{:+.3f}'.format(z) for z in heights[-5:]])            
            #print("sample {:02d} thickness {:.3f}: x:{:+3.0f} y:{:+3.0f}".format(i+1, high-low, spoints[0][0], spoints[0][1]))

            x = abs(max(xcol(spoints)) - min(xcol(spoints)))
            y = abs(max(ycol(spoints)) - min(ycol(spoints)))

            lines.append([
                s_id,
                "{:.3f}".format(high-low), 
                "{:06.3f}".format(x),
                "{:06.3f}".format(y),
                "{:06.3f}".format(np.average(heights)),
                "{:06.3f}".format(np.std(heights))
            ])
    return lines


def print_thinkness_csv(xy_sample, path):

    lines = generate_thinkness_csv(xy_sample)

    for line in lines:
        print(" | ".join(["{:10}".format(c) for c in line]))

    save_thinkness_csv(lines, path)


def print_thinkness_csv_id(xy_sample, x_rows, y_rows, start_id, path):

    lines = generate_thinkness_csv_id(xy_sample, x_rows, y_rows, start_id)

    for line in lines:
        print(" | ".join(["{:10}".format(c) for c in line]))

    csv_path = save_thinkness_csv(lines, path)
    return csv_path


def save_thinkness_csv(lines, path):
    csv_path = build_output_file(path, '', 'csv')
    print("Writing results in csv {}".format(csv_path))
    f = open(csv_path, 'w')
    try:
        for line in lines:
            f.write(",".join(line) + "\n")
        f.write("\n")
    finally:
        f.close()

    return csv_path


def build_output_file(path, suffix, ext):
    prefix = path.rpartition('.')[0]
    if suffix:
        suffix = "-" + suffix
    return '{}{}.{}'.format(prefix, suffix, ext)
