
from sample_measure_lib.draws import *


class ImageHandler:

    def __init__(self, plt, base_path):
        self.plt = plt
        self.base_path = base_path

    def draw_points4_and_save(self, points, name):
        draw_points4(plt, points)
        save_image(self.base_path, name)

    def draw_samples_and_save(self, xy_samples, xy_lows, x_rows, y_rows, name):
        draw_samples(self.plt, xy_samples, xy_lows, x_rows, y_rows)
        save_image(self.base_path, name)


class ImageHandlerNull:

    def __init__(self, plt=None, base_path=None):
        pass

    def draw_points4_and_save(self, points, name):
        pass
    
    def draw_samples_and_save(self, xy_samples, xy_lows, x_rows, y_rows, name):
        pass
