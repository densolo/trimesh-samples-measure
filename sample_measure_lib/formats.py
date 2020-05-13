
from .calcs import *


def fmt3f(f):
    return "{:.3f}".format(f)


def fmt63f(f):
    return "{:+07.3f}".format(f)


def fmt0f(f):
    return "{:.0f}".format(f)


def fmt20f(f):
    return "{:+03.0f}".format(f)


def print_thinkness_csv(xy_samples):
    print("sample,max,x,y")
    for i, spoints in enumerate(xy_samples):
        heights = sorted(zcol(spoints))
        # print(" {} .. {}".format(heights[:5], heights[-5:]))
        low = sum(heights[:100])/100
        high = sum(heights[-50:-10])/40
        #h = '{} .. {}'.format(['{:+.3f}'.format(z) for z in heights[:5]], ['{:+.3f}'.format(z) for z in heights[-5:]])
        #print("sample {:02d} thickness {:.3f}: x:{:+3.0f} y:{:+3.0f}".format(i+1, high-low, spoints[0][0], spoints[0][1]))
        print("{:02},{:.3f},{:+03.0f},{:+03.0f}".format(i+1, high-low, spoints[0][X_AXIS], spoints[0][Y_AXIS]))
