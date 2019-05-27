import os
import pygame

from ShadowWorld import data, resource


def load(filename):
    return pygame.font.Font(data.filepath(os.path.join('fonts', filename)), 12)


class FontResourceCache(resource.ResourceCache):
    def __init__(self):
        super(FontResourceCache, self).__init__()

    def add(self, name):
        self.register(name, load)


FONT_CACHE = FontResourceCache()


def load_fonts():
    g = os.walk(data.filepath('fonts'))
    files = g.__next__()[2]
    for file in files:
        FONT_CACHE.add(file)
        print(file, 'loaded')


def get_font(name):
    return FONT_CACHE.get(name)
