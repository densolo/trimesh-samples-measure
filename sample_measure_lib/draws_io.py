
from sample_measure_lib.draws import *


class ImageHandler:

    def __init__(self, plt, base_path):
        self.plt = plt
        self.base_path = base_path

    def draw_points4_and_save(self, points, name):
        draw_points4(plt, points)
        self.save_image(name)

    def draw_samples_and_save(self, xy_samples, xy_lows, x_rows, y_rows, name, start_id=None):
        draw_samples(self.plt, xy_samples, xy_lows, x_rows, y_rows, start_id=start_id)
        self.save_image(name)

    def draw_image_and_save(self, points, xy_shape, name):
        draw_image(self.plt, points, xy_shape)
        self.save_image(name)

    def show_csv(self, path):
        pass

    def save_image(self, name):
        save_image(self.base_path, name)


class ImageHandlerNull:

    def __init__(self, plt=None, base_path=None):
        pass

    def draw_points4_and_save(self, points, name):
        pass
    
    def draw_samples_and_save(self, xy_samples, xy_lows, x_rows, y_rows, name, start_id=None):
        pass

    def draw_image_and_save(self, xy_samples, x_rows, y_rows, name):
        pass

    def save_image(self, name):
        pass
