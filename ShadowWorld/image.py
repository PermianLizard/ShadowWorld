import os
import pygame

from ShadowWorld import resource, data
from ShadowWorld.consts import TRANSPARENCY_COLOR_KEY, TILE_SIZE


def load(filename):
    img = pygame.image.load(data.filepath(os.path.join('images', filename)))
    img.set_colorkey(TRANSPARENCY_COLOR_KEY)
    return img


def load_images():
    g = os.walk(data.filepath('images'))
    files = g.__next__()[2]
    for file in files:
        CACHE.add(file)
        print(file, 'loaded')


class ImageResourceCache(resource.ResourceCache):
    def __init__(self):
        super(ImageResourceCache, self).__init__()

    def add(self, name):
        self.register(name, load)


class TileResourceCache(ImageResourceCache):
    def __init__(self, tile_size=None):
        super(TileResourceCache, self).__init__()
        self.tile_size = tile_size

    def get_tile(self, name, pos, tile_size=None):
        if tile_size is None:
            tile_size = self.tile_size
        img = self.get(name)
        tw, th = tile_size
        # print (pos[0]*tw, pos[1]*th, tw, th)
        return img.subsurface((pos[0] * tw, pos[1] * th, tw, th))


CACHE = TileResourceCache(tile_size=(TILE_SIZE, TILE_SIZE))


def get(name):
    return CACHE.get(name)


def get_tile(name, pos, tile_size=None):
    return CACHE.get_tile(name, pos, tile_size)
