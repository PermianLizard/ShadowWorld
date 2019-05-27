import os
import sys
import pickle
import zlib

import pygame

from ShadowWorld import controller, dialog, victory, data, util, vec, image, sound, location, entity, phys, ai
from ShadowWorld.consts import *


class GameInstance(object):
    def __init__(self, pc):
        self.pc = pc

        self.locs = {}
        self.current_loc_coords = None
        self.current_pc = None

        self.frame = 0
        self.death_cooldown = -1
        self.win_cooldown = -1

    def init(self):
        self.set_current_loc((0, 0))
        loc = self.get_current_loc()

        for e in loc.entities:
            try:
                if e.player:
                    self.current_pc = e
            except AttributeError:
                pass

    def set_loc(self, loc, coords):
        self.locs[coords] = loc

    def get_loc(self, coords):
        return self.locs.get(coords)

    def get_loc_in_dir(self, dir):
        coords = (self.current_loc_coords[0] + dir[0], self.current_loc_coords[1] + dir[1])
        return self.locs.get(coords)

    def get_current_loc(self):
        return self.get_loc(self.current_loc_coords)

    def set_current_loc(self, coords):
        self.current_loc_coords = coords

    def set_current_loc_to_dir(self, dir):
        coords = (self.current_loc_coords[0] + dir[0], self.current_loc_coords[1] + dir[1])
        self.set_current_loc(coords)


def create_game_instance():
    instance = GameInstance(None)

    for coords, loc in location.load_locs().items():
        instance.set_loc(loc, coords)

    instance.init()

    return instance


GAME_INSTANCE = None

PLAYLIST = ('1.ogg', '2.ogg', '3.ogg')
CURRENT_TRACK = 0


def enter(**kwargs):
    global GAME_INSTANCE

    if kwargs.get('load', False):
        load_game()
    else:
        delete_save()
        GAME_INSTANCE = create_game_instance()

    GAME_INSTANCE.death_cooldown = -1
    GAME_INSTANCE.win_cooldown = -1

    global CURRENT_TRACK
    CURRENT_TRACK = 0

    sound.load_music(PLAYLIST[CURRENT_TRACK])
    sound.play_music()


def exit():
    sound.fadeout_music(100)


def pause():
    pygame.mixer.music.pause()


def unpause(**kwargs):
    pygame.mixer.music.unpause()


def update():
    key = pygame.key.get_pressed()

    global GAME_INSTANCE
    pc = GAME_INSTANCE.current_pc

    player = pc.player
    player.clear()

    control = pc.control
    control.clear()

    if GAME_INSTANCE.death_cooldown > 0:
        GAME_INSTANCE.death_cooldown -= 1
        if GAME_INSTANCE.death_cooldown == 0:
            if has_save():
                controller.swap_scene(sys.modules[__name__], load=True)
            else:
                controller.pop_scene()

    elif GAME_INSTANCE.win_cooldown > 0:
        GAME_INSTANCE.win_cooldown -= 1
        if GAME_INSTANCE.win_cooldown == 0:
            controller.swap_scene(victory)

    else:
        if key[pygame.K_LEFT]:
            pc.control.face_right = False
            pc.control.walk = True
        if key[pygame.K_RIGHT]:
            pc.control.face_right = True
            pc.control.walk = True
        if key[pygame.K_UP]:
            pc.control.face_up = True
            pc.control.climb = True
        if key[pygame.K_DOWN]:
            pc.control.face_down = True
            pc.control.climb = True
        if key[pygame.K_SPACE]:
            pc.control.jump = True

    ai.process(GAME_INSTANCE)

    for evt in phys.process(GAME_INSTANCE):
        if evt.name == 'jump':
            source_entity = evt.source_entity
            try:
                source_entity.player
                sound.play_sound('jump.wav')
            except AttributeError as err:
                print(err )
        elif evt.name == 'bullet-coll':
            bullet = evt.source_entity
            GAME_INSTANCE.get_current_loc().remove_entity(bullet)
            sound.play_sound('bullet-coll.wav')

    for evt in entity.process(GAME_INSTANCE):
        if evt.name == 'death':
            pygame.mixer.music.stop()
            sound.play_sound('death.wav')
            GAME_INSTANCE.death_cooldown = 80
        elif evt.name == 'site':
            effects = evt.effects
            for effect in effects:
                if effect == 'save':
                    save_game()
                    sound.play_sound('save.wav')
                if effect == 'win':
                    pygame.mixer.music.stop()
                    sound.play_sound('win.wav')
                    GAME_INSTANCE.win_cooldown = 80
        elif evt.name == 'bullet-coll':
            bullet = evt.source_entity
            GAME_INSTANCE.get_current_loc().remove_entity(bullet)
            sound.play_sound('bullet-coll.wav')

    loc_dx = player.next_loc_dir[0]
    loc_dy = player.next_loc_dir[1]
    if not loc_dx == 0 or not loc_dy == 0:
        curr_loc = GAME_INSTANCE.get_current_loc()
        next_loc = GAME_INSTANCE.get_loc_in_dir((loc_dx, loc_dy))
        if next_loc is not None:

            pc_curr_til_pos = util.pixel_to_tile(pc.phys.pos)
            pc_next_tile_pos = [0, 0]

            if loc_dy > 0:
                pc_next_tile_pos[1] = 0
            elif loc_dy < 0:
                pc_next_tile_pos[1] = next_loc.map.size[1] - 1
            else:
                pc_next_tile_pos[1] = pc_curr_til_pos[1]

            if loc_dx > 0:
                pc_next_tile_pos[0] = 0
            elif loc_dx < 0:
                pc_next_tile_pos[0] = next_loc.map.size[0] - 1
            else:
                pc_next_tile_pos[0] = pc_curr_til_pos[0]

            pc_next_tile_pos = tuple(pc_next_tile_pos)

            if not next_loc.map.is_pos_blocked(pc_next_tile_pos):
                curr_loc.remove_entity(pc)
                next_loc.add_entity(pc)

                pc.phys.coll.center = util.tile_rect(tuple(pc_next_tile_pos)).center

                GAME_INSTANCE.set_current_loc_to_dir((loc_dx, loc_dy))

    GAME_INSTANCE.frame += 1

    if GAME_INSTANCE.death_cooldown < 0 and GAME_INSTANCE.win_cooldown < 0:
        music_update()


def draw(surf):
    surf.fill((30, 30, 30))

    frame = (GAME_INSTANCE.frame // ANIMATION_SPEED_RATIO) % 3 + 1

    loc = GAME_INSTANCE.get_current_loc()
    loc_map = loc.map

    if not loc_map.render_data:
        loc_map.compile_render_data()

    bg_img = image.get(loc.bg)
    surf.blit(bg_img, (0, 0))

    for y in range(loc_map.size[1]):
        for x in range(loc_map.size[0]):

            tile_render = loc_map.render_data.get((x, y), None)
            if tile_render:
                img = image.get_tile(tile_render[0], tile_render[1])
                surf.blit(img, (x * TILE_SIZE, y * TILE_SIZE))

    loc_entities = loc.entities

    entities = sorted(loc_entities, key=lambda i: i.render.layer)

    for e in entities:
        info = e.info

        if info.kind == 'creature':
            phys = e.phys
            coll = phys.coll

            player = None
            try:
                player = e.player
            except AttributeError:
                pass

            render = e.render
            render_size = render.size
            render_rect = pygame.Rect(coll.topleft, render_size)

            control = e.control

            sprite_tile_pos = (0, 0)

            if phys.grounded:
                if control.walk:
                    sprite_tile_pos = (0, frame)
            if not phys.grounded and phys.hanging:
                sprite_tile_pos = (2, 0)
                if control.climb:
                    sprite_tile_pos = (2, frame)
            if not phys.grounded and not phys.hanging:
                sprite_tile_pos = (1, frame)

            if player:
                if not player.alive:
                    player.death_frame += 1
                    if player.death_frame < 3:
                        sprite_tile_pos = (3, player.death_frame)
                    else:
                        sprite_tile_pos = (3, 0)

            img = image.get_tile(render.spritesheet, sprite_tile_pos, render_size)

            if control.face_right:
                img = pygame.transform.flip(img, True, False)

            surf.blit(img, render_rect)

        if info.kind == 'liquid':
            phys = e.phys
            coll = phys.coll

            render = e.render
            render_size = render.size
            render_rect = pygame.Rect(coll.topleft, render_size)

            tile_pos = util.pixel_to_tile(phys.pos)
            tile_pos_above = vec.add(tile_pos, (0, -1))

            sprite_tile_pos = (0, 0)

            if loc_map.is_pos_legal(tile_pos_above) and not loc_map.is_pos_blocked(tile_pos_above):
                sprite_tile_pos = (0, frame)
                for oe in entities:
                    if util.pixel_to_tile(oe.phys.pos) == tile_pos_above:
                        if oe.info.kind == 'liquid':
                            sprite_tile_pos = (0, 0)

            img = image.get_tile(render.spritesheet, sprite_tile_pos, render_size)
            surf.blit(img, render_rect)

        if info.kind == 'bullet':
            phys = e.phys
            coll = phys.coll

            render = e.render
            render_size = render.size
            render_rect = pygame.Rect(coll.topleft, render_size)

            tile_pos = util.pixel_to_tile(phys.pos)

            img = image.get_tile(render.spritesheet, (0, 0), render_size)
            surf.blit(img, render_rect)

        if info.kind == 'site':
            phys = e.phys
            coll = phys.coll

            render = e.render
            render_size = render.size
            render_rect = pygame.Rect(coll.topleft, render_size)

            tile_pos = util.pixel_to_tile(phys.pos)

            img = image.get_tile(render.spritesheet, (0, 0), render_size)
            surf.blit(img, render_rect)


def on_key_down(key, mod):
    if GAME_INSTANCE.death_cooldown < 0 and GAME_INSTANCE.win_cooldown < 0:
        if key == pygame.K_ESCAPE:
            controller.push_scene(dialog)


def on_key_up(key, mod):
    pass


def on_mouse_motion(pos, rel, buttons):
    pass


def on_mouse_button_down(pos, button):
    pass


def on_mouse_button_up(pos, button):
    pass


def save_game():
    with open(data.filepath(SAVE_FILE), 'wb') as f:
        f.write(zlib.compress(pickle.dumps(GAME_INSTANCE, pickle.HIGHEST_PROTOCOL), 9))


def load_game():
    filename = data.filepath(SAVE_FILE)
    if has_save():
        with open(filename, 'rb') as f:
            pk = zlib.decompress(f.read())

            global GAME_INSTANCE
            GAME_INSTANCE = pickle.loads(pk)


def delete_save():
    filename = data.filepath(SAVE_FILE)
    if has_save():
        os.remove(data.filepath(SAVE_FILE))


def has_save():
    filename = data.filepath(SAVE_FILE)
    return os.path.isfile(filename)


def music_update():
    if not pygame.mixer.music.get_busy():
        global CURRENT_TRACK
        CURRENT_TRACK += 1
        CURRENT_TRACK %= len(PLAYLIST)

        sound.load_music(PLAYLIST[CURRENT_TRACK])
        sound.play_music()


if __name__ == '__main__':
    import sys
    import controller

    controller.run(sys.modules[__name__])
