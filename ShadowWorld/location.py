import configparser
import os

from ShadowWorld import data, entity, util
from ShadowWorld.consts import *


class Location(object):
    def __init__(self, map, bg):
        self.map = map
        self.entities = []
        self.bg = bg

    def add_entity(self, e):
        self.entities.append(e)

    def remove_entity(self, e):
        self.entities.remove(e)


class Map(object):
    def __init__(self, size, data=None):
        self.size = size
        if data:
            self.data = data
        else:
            self.data = util.create_matrix(size)

        self.render_data = None
        self.compile_render_data()

    def get_tile(self, pos):
        return self.data[pos[1]][pos[0]]

    def set_tile(self, pos, tile):
        self.data[pos[1]][pos[0]] = tile

    def is_pos_legal(self, pos):
        if pos[0] < 0 or pos[1] < 0:
            return False
        if pos[0] > self.size[0] - 1:
            return False
        if pos[1] > self.size[1] - 1:
            return False
        return True

    def is_pos_blocked(self, pos):
        if not self.is_pos_legal(pos):
            return True
        tile = self.get_tile(pos)
        if tile is not None:
            if 'solid' in tile.tile_type:
                return True
        return False

    def compile_render_data(self):
        size = self.size

        render_data = {}

        for y in range(size[1]):
            for x in range(size[0]):
                tile = self.get_tile((x, y))
                if tile is None:
                    continue

                if 'none' in tile.tile_type:
                    continue

                neighbor_group_data = util.create_matrix((3, 3), False)
                for i in range(3):
                    for j in range(3):
                        ny = y - 1 + i
                        nx = x - 1 + j

                        if nx < 0 or ny < 0 or nx >= size[0] or ny >= size[1]:
                            neighbor_group_data[i][j] = True
                        else:
                            try:
                                n_tile = self.get_tile((nx, ny))
                                if n_tile is None:
                                    neighbor_group_data[i][j] = False
                                elif 'none' in n_tile.tile_type:
                                    neighbor_group_data[i][j] = False
                                elif n_tile and (
                                        n_tile.tile_group == tile.tile_group or n_tile.tile_group in tile.tile_group_tolerance):
                                    neighbor_group_data[i][j] = True
                            except AttributeError:
                                neighbor_group_data[i][j] = False

                tileset_index_key = (neighbor_group_data[0][0], neighbor_group_data[0][1], neighbor_group_data[0][2],
                                     neighbor_group_data[1][0], neighbor_group_data[1][2],
                                     neighbor_group_data[2][0], neighbor_group_data[2][1], neighbor_group_data[2][2])

                tileset_index = TILESET_INDEX_MAP[tileset_index_key]

                render_data[(x, y)] = (tile.tileset, tileset_index)

        self.render_data = render_data


class Tile(object):
    def __init__(self, **kwargs):
        self.entity_props = {}

        for k, v in kwargs.items():

            if k == 'tile_type':
                self.__setattr__(k, v.split())
            if k == 'tile_group':
                self.__setattr__(k, int(v))
            elif k == 'tile_group_tolerance':
                self.__setattr__(k, [int(i) for i in v.split()])
            if k.startswith('entity_'):
                self.entity_props[k[k.index('_') + 1:]] = v
            else:
                self.__setattr__(k, v)


def load_locs():
    locs = {}

    g = os.walk(data.filepath('locs'))
    files = g.__next__()[2]

    for file in files:
        parts = file.split('_')
        coords = tuple([int(v) for v in (parts[0], (parts[1].split('.')[0]))])
        locs[coords] = load_loc(data.filepath(os.path.join('locs', file)))

    return locs


def load_loc(filename):
    print('loading loc:', filename)

    parser = configparser.ConfigParser()
    parser.read(filename)

    map_data = parser.get('map', 'data')
    map_bg = parser.get('map', 'bg')
    map = Map(MAP_SIZE)

    tiles = {}
    for section in parser.sections():
        if len(section) == 1:
            print(section, parser.items(section))

            desc = {}
            tiles[section] = Tile(**dict(parser.items(section)))

    # place tiles
    for i, row in enumerate(map_data.split('\n')):
        for j, c in enumerate(row):
            if c not in ' .':
                tile = tiles[c]
                assert tile

                map.set_tile((j, i), tile)

    loc = Location(map, map_bg)

    # place entities
    for i in range(MAP_SIZE[1]):
        for j in range(MAP_SIZE[0]):
            tile = map.get_tile((j, i))
            if tile:
                if len(tile.entity_props) > 0:
                    e_args = dict(tile.entity_props)

                    print('entity to make ID:', e_args['id'])

                    pos = util.tile_entity_pos((j, i))
                    e_args['pos'] = pos
                    loc.add_entity(entity.make(**e_args))

    return loc


TILESET_INDEX_MAP = {(True, False, False, False, True, False, False, False): (8, 8),
                     (False, False, False, False, True, False, False, False): (8, 0),
                     (True, False, False, False, True, True, True, True): (15, 8),
                     (False, True, True, True, False, True, False, True): (5, 7),
                     (False, True, True, False, False, True, True, False): (6, 6),
                     (False, True, True, False, True, True, True, False): (14, 6),
                     (True, True, True, True, True, True, False, True): (13, 15),
                     (True, False, True, False, True, True, True, False): (14, 10),
                     (False, False, True, False, True, True, True, False): (14, 2),
                     (False, False, True, False, True, False, False, True): (9, 2),
                     (True, False, False, False, False, False, True, False): (2, 8),
                     (False, True, False, False, False, True, True, False): (6, 4),
                     (False, True, False, True, False, True, False, True): (5, 5),
                     (True, True, False, True, True, True, True, True): (15, 13),
                     (True, False, True, True, False, False, False, False): (0, 11),
                     (True, True, True, False, True, False, True, True): (11, 14),
                     (True, False, True, False, False, False, False, True): (1, 10),
                     (False, False, True, False, False, True, False, False): (4, 2),
                     (True, True, True, False, True, True, False, False): (12, 14),
                     (False, True, True, True, True, False, True, False): (10, 7),
                     (True, True, False, True, False, False, True, False): (2, 13),
                     (False, False, True, False, False, False, True, True): (3, 2),
                     (False, False, False, False, False, True, False, True): (5, 0),
                     (True, False, False, True, False, False, True, False): (2, 9),
                     (True, False, True, False, True, True, False, False): (12, 10),
                     (False, True, False, True, True, True, False, True): (13, 5),
                     (False, True, True, True, True, False, False, False): (8, 7),
                     (True, False, True, False, True, False, True, True): (11, 10),
                     (True, False, True, True, True, False, True, False): (10, 11),
                     (True, False, False, True, True, True, True, True): (15, 9),
                     (False, True, True, True, True, True, True, True): (15, 7),
                     (False, False, True, True, False, True, True, False): (6, 3),
                     (True, True, False, False, False, False, True, False): (2, 12),
                     (False, True, False, False, True, False, True, True): (11, 4),
                     (True, False, False, True, True, False, False, False): (8, 9),
                     (True, True, True, True, False, True, True, False): (6, 15),
                     (False, False, False, False, True, True, False, True): (13, 0),
                     (True, False, True, True, True, True, False, True): (13, 11),
                     (False, True, False, False, True, True, False, False): (12, 4),
                     (False, True, True, True, False, False, True, False): (2, 7),
                     (True, True, False, False, True, True, True, True): (15, 12),
                     (False, False, True, True, True, True, True, False): (14, 3),
                     (False, False, False, True, True, False, True, True): (11, 1),
                     (True, True, False, False, True, False, False, False): (8, 12),
                     (False, True, False, False, False, False, False, True): (1, 4),
                     (True, True, True, True, False, True, True, True): (7, 15),
                     (False, True, False, True, False, False, False, False): (0, 5),
                     (False, False, False, True, True, True, False, False): (12, 1),
                     (True, False, True, True, False, True, False, True): (5, 11),
                     (False, True, True, False, False, False, True, False): (2, 6),
                     (False, True, False, True, False, True, True, True): (7, 5),
                     (True, False, True, False, False, False, True, False): (2, 10),
                     (True, True, True, False, True, False, False, True): (9, 14),
                     (False, False, False, True, False, False, False, True): (1, 1),
                     (True, False, False, False, False, True, True, False): (6, 8),
                     (True, False, False, True, False, True, False, True): (5, 9),
                     (False, False, False, False, False, False, False, False): (0, 0),
                     (True, True, True, False, False, True, True, True): (7, 14),
                     (False, True, False, True, True, False, True, False): (10, 5),
                     (False, True, False, False, True, True, False, True): (13, 4),
                     (False, False, False, False, False, True, True, True): (7, 0),
                     (False, True, True, False, True, False, False, False): (8, 6),
                     (True, True, True, False, False, True, False, False): (4, 14),
                     (False, False, True, True, False, False, True, True): (3, 3),
                     (True, True, False, True, False, True, True, False): (6, 13),
                     (True, True, False, False, False, True, False, True): (5, 12),
                     (False, False, True, True, False, True, False, False): (4, 3),
                     (True, True, True, True, True, False, False, False): (8, 15),
                     (False, False, False, False, True, False, True, False): (10, 0),
                     (True, False, False, True, True, True, False, True): (13, 9),
                     (True, True, False, True, True, False, False, False): (8, 13),
                     (True, True, True, False, True, True, True, False): (14, 14),
                     (True, False, True, True, True, False, False, False): (8, 11),
                     (False, True, False, False, True, False, False, True): (9, 4),
                     (False, True, True, True, False, True, True, True): (7, 7),
                     (False, False, True, True, True, False, False, True): (9, 3),
                     (True, False, True, True, True, True, True, True): (15, 11),
                     (True, False, True, True, False, True, True, True): (7, 11),
                     (True, False, False, False, True, False, True, True): (11, 8),
                     (True, True, False, False, True, True, False, True): (13, 12),
                     (False, True, False, False, False, True, False, False): (4, 4),
                     (True, False, False, False, True, True, False, False): (12, 8),
                     (False, False, False, True, True, False, False, True): (9, 1),
                     (True, False, True, True, False, False, True, False): (2, 11),
                     (False, True, False, False, False, False, True, True): (3, 4),
                     (False, True, True, False, False, True, False, True): (5, 6),
                     (True, True, True, False, False, False, False, False): (0, 14),
                     (True, True, True, True, True, True, True, False): (14, 15),
                     (True, True, True, True, True, True, True, True): (15, 15),
                     (True, True, False, True, True, False, True, True): (11, 13),
                     (False, False, True, False, True, False, True, False): (10, 2),
                     (True, False, False, False, False, False, False, True): (1, 8),
                     (False, False, False, True, False, True, False, False): (4, 1),
                     (True, False, False, True, False, False, False, False): (0, 9),
                     (True, True, False, True, True, True, False, False): (12, 13),
                     (False, False, False, True, False, False, True, True): (3, 1),
                     (True, False, False, True, False, True, True, True): (7, 9),
                     (False, False, True, False, False, True, True, True): (7, 2),
                     (False, True, True, False, True, True, False, True): (13, 6),
                     (True, False, True, True, True, False, True, True): (11, 11),
                     (True, False, True, False, True, True, True, True): (15, 10),
                     (True, True, False, True, False, False, False, True): (1, 13),
                     (False, False, True, False, False, False, False, False): (0, 2),
                     (True, True, False, False, False, False, False, False): (0, 12),
                     (False, False, True, True, False, False, False, True): (1, 3),
                     (True, False, False, True, True, False, True, False): (10, 9),
                     (False, True, False, True, True, True, True, False): (14, 5),
                     (True, True, False, False, False, True, True, True): (7, 12),
                     (False, True, False, False, True, True, True, False): (14, 4),
                     (True, False, True, False, True, False, False, False): (8, 10),
                     (True, True, True, True, False, False, True, True): (3, 15),
                     (False, True, True, True, True, True, False, False): (12, 7),
                     (False, False, True, True, True, True, False, False): (12, 3),
                     (True, True, True, True, False, True, False, False): (4, 15),
                     (True, True, False, False, True, False, True, False): (10, 12),
                     (False, False, True, True, True, False, True, True): (11, 3),
                     (False, False, False, True, True, True, True, False): (14, 1),
                     (True, False, False, False, True, False, False, True): (9, 8),
                     (False, True, True, True, False, False, False, True): (1, 7),
                     (False, True, True, False, False, False, False, False): (0, 6),
                     (False, False, True, False, True, True, False, True): (13, 2),
                     (False, True, True, False, False, True, True, True): (7, 6),
                     (True, False, False, False, False, True, False, False): (4, 8),
                     (False, True, False, True, False, False, True, True): (3, 5),
                     (False, True, True, True, True, False, True, True): (11, 7),
                     (True, False, False, False, False, False, True, True): (3, 8),
                     (True, False, True, False, False, True, False, True): (5, 10),
                     (False, True, False, True, False, True, False, False): (4, 5),
                     (False, True, True, False, True, False, True, False): (10, 6),
                     (True, True, True, False, True, False, True, False): (10, 14),
                     (True, True, False, True, False, True, False, False): (4, 13),
                     (False, False, True, False, False, True, False, True): (5, 2),
                     (False, False, False, False, False, False, True, True): (3, 0),
                     (False, True, False, True, True, False, False, True): (9, 5),
                     (True, True, False, True, False, False, True, True): (3, 13),
                     (False, False, False, False, False, True, False, False): (4, 0),
                     (False, True, True, False, False, False, True, True): (3, 6),
                     (False, False, False, True, False, True, True, False): (6, 1),
                     (True, False, True, False, True, True, False, True): (13, 10),
                     (True, False, True, False, False, False, True, True): (3, 10),
                     (True, True, True, False, False, False, True, True): (3, 14),
                     (False, True, True, True, True, False, False, True): (9, 7),
                     (True, True, True, True, False, False, False, True): (1, 15),
                     (False, False, False, False, True, False, False, True): (9, 0),
                     (True, False, False, True, True, True, True, False): (14, 9),
                     (True, False, False, False, True, True, True, False): (14, 8),
                     (False, True, False, False, True, False, True, False): (10, 4),
                     (False, True, True, True, False, True, False, False): (4, 7),
                     (True, False, True, True, True, True, False, False): (12, 11),
                     (True, True, True, True, True, True, False, False): (12, 15),
                     (False, True, True, True, False, False, True, True): (3, 7),
                     (False, False, True, False, True, False, False, False): (8, 2),
                     (True, True, False, False, True, True, True, False): (14, 12),
                     (False, True, False, False, False, True, True, True): (7, 4),
                     (True, True, False, True, True, False, False, True): (9, 13),
                     (True, True, False, True, True, True, True, False): (14, 13),
                     (False, False, False, True, True, False, True, False): (10, 1),
                     (True, False, True, True, False, False, False, True): (1, 11),
                     (False, True, False, False, False, False, False, False): (0, 4),
                     (False, False, False, False, True, True, True, False): (14, 0),
                     (False, True, False, True, False, False, False, True): (1, 5),
                     (True, True, True, True, True, False, True, True): (11, 15),
                     (True, True, True, False, True, True, False, True): (13, 14),
                     (True, False, True, False, False, True, True, True): (7, 10),
                     (False, False, True, False, False, False, True, False): (2, 2),
                     (True, False, False, True, False, False, True, True): (3, 9),
                     (False, True, False, True, True, True, False, False): (12, 5),
                     (False, False, False, True, False, False, False, False): (0, 1),
                     (True, False, False, True, False, True, False, False): (4, 9),
                     (False, False, False, False, False, False, False, True): (1, 0),
                     (True, False, True, False, True, False, True, False): (10, 10),
                     (False, True, False, True, True, False, True, True): (11, 5),
                     (False, True, True, True, True, True, True, False): (14, 7),
                     (True, True, True, False, False, True, False, True): (5, 14),
                     (True, True, False, False, False, False, True, True): (3, 12),
                     (False, False, True, True, False, False, True, False): (2, 3),
                     (True, False, False, True, True, False, False, True): (9, 9),
                     (False, False, False, False, True, True, False, False): (12, 0),
                     (True, True, False, False, False, True, False, False): (4, 12),
                     (False, False, True, False, True, True, True, True): (15, 2),
                     (False, False, False, False, True, False, True, True): (11, 0),
                     (True, True, True, False, True, True, True, True): (15, 14),
                     (True, True, True, True, False, False, False, False): (0, 15),
                     (False, False, True, True, True, True, True, True): (15, 3),
                     (True, False, True, True, True, False, False, True): (9, 11),
                     (True, True, False, False, True, False, False, True): (9, 12),
                     (False, False, True, True, True, False, False, False): (8, 3),
                     (False, False, False, True, True, True, False, True): (13, 1),
                     (True, False, False, False, True, False, True, False): (10, 8),
                     (True, False, True, True, False, True, False, False): (4, 11),
                     (False, True, False, False, False, True, False, True): (5, 4),
                     (False, True, False, True, False, True, True, False): (6, 5),
                     (True, False, True, False, False, False, False, False): (0, 10),
                     (True, False, True, True, False, False, True, True): (3, 11),
                     (False, True, True, False, False, True, False, False): (4, 6),
                     (True, True, True, False, True, False, False, False): (8, 14),
                     (True, False, False, False, False, True, True, True): (7, 8),
                     (True, True, False, True, True, False, True, False): (10, 13),
                     (True, False, False, False, False, False, False, False): (0, 8),
                     (False, False, False, False, False, False, True, False): (2, 0),
                     (False, False, False, True, False, True, False, True): (5, 1),
                     (False, False, False, False, False, True, True, False): (6, 0),
                     (True, False, False, True, False, False, False, True): (1, 9),
                     (False, True, True, False, True, False, False, True): (9, 6),
                     (True, False, True, False, True, False, False, True): (9, 10),
                     (True, False, True, True, False, True, True, False): (6, 11),
                     (True, True, False, True, False, True, True, True): (7, 13),
                     (False, False, True, False, False, True, True, False): (6, 2),
                     (False, False, True, True, False, True, False, True): (5, 3),
                     (True, False, False, True, True, True, False, False): (12, 9),
                     (True, True, False, True, False, False, False, False): (0, 13),
                     (True, True, False, False, False, False, False, True): (1, 12),
                     (False, True, False, False, True, False, False, False): (8, 4),
                     (True, False, False, True, True, False, True, True): (11, 9),
                     (True, True, True, True, True, False, False, True): (9, 15),
                     (True, False, True, True, True, True, True, False): (14, 11),
                     (False, True, False, False, True, True, True, True): (15, 4),
                     (True, True, True, True, False, False, True, False): (2, 15),
                     (True, True, False, False, True, True, False, False): (12, 12),
                     (False, False, True, True, True, True, False, True): (13, 3),
                     (True, True, True, False, False, False, False, True): (1, 14),
                     (True, False, False, False, True, True, False, True): (13, 8),
                     (False, False, False, True, True, False, False, False): (8, 1),
                     (True, True, False, False, True, False, True, True): (11, 12),
                     (False, True, False, False, False, False, True, False): (2, 4),
                     (True, True, True, False, False, False, True, False): (2, 14),
                     (False, False, False, True, True, True, True, True): (15, 1),
                     (False, True, True, True, False, False, False, False): (0, 7),
                     (False, False, True, False, True, False, True, True): (11, 2),
                     (False, True, True, False, False, False, False, True): (1, 6),
                     (True, True, False, True, True, True, False, True): (13, 13),
                     (False, False, True, False, True, True, False, False): (12, 2),
                     (False, False, False, True, False, False, True, False): (2, 1),
                     (True, False, False, False, False, True, False, True): (5, 8),
                     (True, False, False, True, False, True, True, False): (6, 9),
                     (False, True, False, True, False, False, True, False): (2, 5),
                     (False, True, True, False, True, True, False, False): (12, 6),
                     (True, False, True, False, False, True, False, False): (4, 10),
                     (False, False, True, False, False, False, False, True): (1, 2),
                     (False, True, True, False, True, False, True, True): (11, 6),
                     (False, True, True, True, False, True, True, False): (6, 7),
                     (False, False, True, True, False, False, False, False): (0, 3),
                     (False, True, False, True, True, True, True, True): (15, 5),
                     (True, False, True, False, False, True, True, False): (6, 10),
                     (True, True, False, True, False, True, False, True): (5, 13),
                     (True, True, False, False, False, True, True, False): (6, 12),
                     (False, False, True, True, False, True, True, True): (7, 3),
                     (False, False, False, False, True, True, True, True): (15, 0),
                     (False, True, False, True, True, False, False, False): (8, 5),
                     (True, True, True, True, True, False, True, False): (10, 15),
                     (False, True, True, True, True, True, False, True): (13, 7),
                     (True, True, True, False, False, True, True, False): (6, 14),
                     (True, True, True, True, False, True, False, True): (5, 15),
                     (False, False, False, True, False, True, True, True): (7, 1),
                     (False, False, True, True, True, False, True, False): (10, 3),
                     (False, True, True, False, True, True, True, True): (15, 6)}

if __name__ == '__main__':
    load_locs()
