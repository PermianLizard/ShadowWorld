import pygame

from ShadowWorld.consts import TILE_SIZE


def create_matrix(size, value=None):
    matrix = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(value)
        matrix.append(row)
    return matrix


def pixel_to_tile(pixel):
    return pixel[0] // TILE_SIZE, pixel[1] // TILE_SIZE


def tile_to_pixel(tile):
    return tile[0] * TILE_SIZE, tile[1] * TILE_SIZE


def tile_rect(tile):
    pixel_pos = tile_to_pixel(tile)
    return pygame.Rect(pixel_pos[0], pixel_pos[1], TILE_SIZE, TILE_SIZE)


def tile_entity_pos(tile):
    return tile_rect(tile).center
