import pygame
import random

from ShadowWorld import entity
from ShadowWorld import util


def process(gameInstance):
    loc = gameInstance.get_current_loc()

    for e in loc.entities:
        try:
            thought = e.thought

            for behavior in thought.behavior:
                BEHAVIOR_MAP[behavior](gameInstance, e)


        except AttributeError:
            continue


def patrol(gameInstance, e):
    loc = gameInstance.get_current_loc()
    map = loc.map

    phys = e.phys
    coll = phys.coll

    control = e.control

    if control.face_right:
        check_pos = coll.right + 1, coll.centery
    else:
        check_pos = coll.left - 1, coll.centery

    check_pos_tile_pos = util.pixel_to_tile(check_pos)

    if map.is_pos_legal(check_pos_tile_pos):
        if map.is_pos_blocked(check_pos_tile_pos):
            control.face_left = not control.face_left
        else:
            down_check_pos_tile_pos = check_pos_tile_pos[0], check_pos_tile_pos[1] + 1
            if map.is_pos_legal(down_check_pos_tile_pos):
                if not map.is_pos_blocked(down_check_pos_tile_pos):
                    control.face_left = not control.face_left
    else:
        control.face_left = not control.face_left

    control.walk = True


def random_patrol(gameInstance, e):
    loc = gameInstance.get_current_loc()
    map = loc.map

    phys = e.phys
    coll = phys.coll

    control = e.control

    if control.face_right:
        check_pos = coll.right + 1, coll.centery
    else:
        check_pos = coll.left - 1, coll.centery

    check_pos_tile_pos = util.pixel_to_tile(check_pos)

    turn = False

    if map.is_pos_legal(check_pos_tile_pos):
        if map.is_pos_blocked(check_pos_tile_pos):
            control.face_left = not control.face_left
            turn = True
        else:
            down_check_pos_tile_pos = check_pos_tile_pos[0], check_pos_tile_pos[1] + 1
            if map.is_pos_legal(down_check_pos_tile_pos):
                if not map.is_pos_blocked(down_check_pos_tile_pos):
                    control.face_left = not control.face_left
                    turn = True
    else:
        control.face_left = not control.face_left
        turn = True

    if not turn:
        if random.random() > .98:
            control.face_left = not control.face_left

    control.walk = True


def shoot(gameInstance, e):
    loc = gameInstance.get_current_loc()
    map = loc.map

    phys = e.phys
    coll = phys.coll

    control = e.control

    if gameInstance.frame % 20 == 0:

        check_rect = pygame.Rect(coll.center, (256, 16))
        if control.face_right:
            check_rect.left = coll.right
        else:
            check_rect.right = coll.left

        for ent in loc.entities:
            if ent is e:
                continue

            if ent.info.kind == 'creature':
                try:
                    ent.player

                    if check_rect.colliderect(ent.phys.coll):
                        bullet = entity.make_bullet(pos=phys.pos, face_right='true' if control.face_right else 'false')
                        loc.entities.append(bullet)

                except AttributeError:
                    pass


def match_jump(gameInstance, e):
    loc = gameInstance.get_current_loc()
    map = loc.map

    phys = e.phys
    coll = phys.coll

    control = e.control

    control.jump = False

    check_rect = pygame.Rect((0, 0), (64, 32))
    check_rect.bottom = coll.bottom
    if control.face_right:
        check_rect.left = coll.right
    else:
        check_rect.right = coll.left

    for ent in loc.entities:
        if ent is e:
            continue

        if ent.info.kind == 'creature':
            try:
                ent.player

                if check_rect.colliderect(ent.phys.coll):
                    if coll.centery > ent.phys.coll.centery:
                        control.jump = True

            except AttributeError:
                pass


BEHAVIOR_MAP = {'patrol': patrol,
                'random_patrol': random_patrol,
                'shoot': shoot,
                'match_jump': match_jump}
