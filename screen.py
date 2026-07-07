import pygame as pg

class Screen():
    def __init__(self):
        self.screen_info = pg.display.Info()
        self.width = self.save_width = self.screen_info.current_w
        self.height = self.save_height = self.screen_info.current_h
        self.set_size(self.width, self.height)

    def set_size(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.surface = pg.display.set_mode((self.width, self.height))

    def update(self, new_width, new_height):
        self.set_size(new_width, new_height)