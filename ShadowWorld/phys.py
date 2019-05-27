from ShadowWorld import vec, util
from ShadowWorld.consts import *
from ShadowWorld.event import Event

GRAVITY = (0, 1)


def process(gameInstance):
    loc = gameInstance.get_current_loc()
    map = loc.map

    events = []

    for e in loc.entities:

        info = e.info
        if info.kind in ('creature', 'bullet'):

            phys = e.phys
            control = e.control
            stats = e.stats

            coll = phys.coll.copy()
            vel = phys.vel

            if not phys.hanging:
                if info.kind == 'creature':
                    vel = vec.add(vel, GRAVITY)
                elif info.kind == 'bullet':
                    if control.face_right:
                        vel = vec.add(vel, (2, 0))
                    else:
                        vel = vec.add(vel, (-2, 0))

            if control.jump:
                if phys.grounded:
                    vel = vec.add(vel, (0, -stats.jump_strength))
                    events.append(Event('jump', source_entity=e))
                elif phys.hanging:
                    if control.face_right:
                        vel = vec.add(vel, (-stats.jump_strength, -stats.jump_strength))
                    else:
                        vel = vec.add(vel, (stats.jump_strength, -stats.jump_strength))

            if control.walk:
                if phys.grounded:
                    if control.face_right:
                        vel = vec.add(vel, (stats.walk_speed, 0))
                    else:
                        vel = vec.add(vel, (-stats.walk_speed, 0))
                elif phys.hanging:
                    if control.face_up:
                        vel = vec.add(vel, (0, 1))
                    else:
                        vel = vec.add(vel, (0, -1))
                else:
                    if control.face_right:
                        vel = vec.add(vel, (1, 0))
                    else:
                        vel = vec.add(vel, (-1, 0))

            if control.climb:
                if phys.hanging:
                    if control.face_up:
                        vel = vec.add(vel, (0, -stats.walk_speed))
                    else:
                        vel = vec.add(vel, (0, stats.walk_speed))

            vel = vec.limit(vel, MAX_SPEED)
            coll.center = vec.add(coll.center, vel)

            coll_checks = []
            coll_dir = {DIR_UP: False, DIR_LEFT: False, DIR_DOWN: False, DIR_RIGHT: False}

            if vel[0] < 0:
                coll_checks.append((coll.midleft, DIR_LEFT))

            elif vel[0] > 0:
                coll_checks.append((coll.midright, DIR_RIGHT))

            if vel[1] < 0:
                coll_checks.append((coll.midtop, DIR_UP))

            elif vel[1] > 0:
                coll_checks.append((coll.midbottom, DIR_DOWN))

            for point, dir in coll_checks:
                coll_type = 'none'

                tile_pos = util.pixel_to_tile(point)
                if map.is_pos_legal(tile_pos):
                    tile = map.get_tile(tile_pos)
                    if tile is not None:
                        coll_type = tile.tile_type
                else:
                    coll_type = 'solid'

                tile_rect = util.tile_rect(tile_pos)

                if coll.colliderect(tile_rect):

                    # level switching
                    if not map.is_pos_legal(tile_pos):
                        try:
                            player = e.player
                            if dir == DIR_LEFT:
                                player.next_loc_dir[0] = -1
                            elif dir == DIR_RIGHT:
                                player.next_loc_dir[0] = 1

                            if dir == DIR_UP:
                                player.next_loc_dir[1] = -1
                            elif dir == DIR_DOWN:
                                player.next_loc_dir[1] = 1

                        except AttributeError:
                            pass

                    if coll_type == 'solid':
                        coll_dir[dir] = True
                        if dir == DIR_UP:
                            coll.top = tile_rect.bottom
                            vel = vel[0], 0
                        elif dir == DIR_LEFT:
                            coll.left = tile_rect.right
                            vel = 0, vel[1]
                        elif dir == DIR_DOWN:
                            coll.bottom = tile_rect.top
                            vel = vel[0], 0
                        elif dir == DIR_RIGHT:
                            coll.right = tile_rect.left
                            vel = 0, vel[1]

            if info.kind == 'bullet':
                for k, v in coll_dir.items():
                    if v:
                        events.append(Event('bullet-coll', source_entity=e))

            grounded = False
            if coll_dir[DIR_DOWN]:
                if coll.bottom % TILE_SIZE == 0:
                    tile_pos = util.pixel_to_tile(phys.coll.midbottom)
                    if map.is_pos_legal(tile_pos):
                        tile = map.get_tile(tile_pos)
                        if tile is not None and ('solid' in tile.tile_type or 'cloud' in tile.tile_type):
                            grounded = True

            hanging = False

            if control.can_climb:
                dir = DIR_RIGHT if control.face_right else DIR_LEFT
                tile_pos = None
                if dir == DIR_RIGHT:
                    if coll.right % TILE_SIZE == 0:
                        tile_pos = util.pixel_to_tile(phys.coll.midright)
                else:
                    if coll.left % TILE_SIZE == 0:
                        tile_pos = util.pixel_to_tile(phys.coll.midleft)
                        tile_pos = tile_pos[0] - 1, tile_pos[1]
                if tile_pos and map.is_pos_legal(tile_pos):
                    tile = map.get_tile(tile_pos)
                    if tile is not None and 'solid' in tile.tile_type:
                        hanging = True

            if grounded:
                vel = 0, vel[1]
                phys.face_up = True

            if hanging:
                vel = vel[0], 0
            elif phys.hanging:
                if control.face_up:
                    if control.walk and not control.jump:
                        if control.face_right:
                            vel = 5, -3
                        else:
                            vel = -5, -3

            if not grounded and not hanging:
                if vel[0] > 0:
                    vel = vec.sub(vel, (1, 0))
                if vel[0] < 0:
                    vel = vec.add(vel, (1, 0))

            phys.vel = vel
            phys.coll.center = coll.center
            phys.grounded = grounded
            phys.hanging = hanging

    return events
