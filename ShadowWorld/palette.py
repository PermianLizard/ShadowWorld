import os

import data
import resource


def load(filename):
    palette = []
    with open(data.filepath(os.path.join('palettes', filename))) as f:
        for i, line in enumerate(f.readlines()):
            if i > 4:
                fields = line.split()
                color = tuple([int(v) for v in fields[:-1]])
                palette.append(color)

    return tuple(palette)


def interpolate(p1, p2, perc):
    if perc == 0.0:
        return p1
    if perc == 1.0:
        return p2

    newpal = []
    for color1, color2 in zip(p1, p2):
        newcol = []
        for j in xrange(3):
            v1, v2 = color1[j], color2[j]
            if v1 == v2:
                newcol.append(v1)
            else:
                mod = int((v2 - v1) * perc)
                newcol.append(v1 + mod)

        newpal.append(tuple(newcol))

    return tuple(newpal)


class PaletteResourceCache(resource.ResourceCache):
    def __init__(self):
        super(PaletteResourceCache, self).__init__()

    def add(self, name):
        self.register(name, load)


def alternator(start_pal, pal1, pal2, inc):
    accum = .0
    curr = start_pal
    next = pal1
    start = True

    while True:
        accum += inc
        if accum >= 1.0:
            accum = .0
            if start:
                curr = pal1
                next = pal2
                start = False
            else:
                curr, next = next, curr
        yield interpolate(curr, next, accum)
