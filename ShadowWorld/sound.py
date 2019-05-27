import os
import pygame

from ShadowWorld import resource, data


def load(filename):
    return pygame.mixer.Sound(data.filepath(os.path.join('sounds', filename)))


def load_sounds():
    g = os.walk(data.filepath('sounds'))
    files = g.__next__()[2]
    for file in files:
        SOUND_CACHE.add(file)
        print(file, 'loaded')


class SoundResourceCache(resource.ResourceCache):
    def __init__(self):
        super(SoundResourceCache, self).__init__()

    def add(self, name):
        self.register(name, load)


SOUND_CACHE = SoundResourceCache()


def get_sound(name):
    return SOUND_CACHE.get(name)


def play_sound(name):
    return SOUND_CACHE.get(name).play()


def load_music(name):
    pygame.mixer.music.load(data.filepath(os.path.join('music', name)))


def play_music():
    pygame.mixer.music.play()


def stop_music():
    pygame.mixer.music.stop()


def fadeout_music(time):
    pygame.mixer.music.fadeout(time)
