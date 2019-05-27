import pygame

from ShadowWorld.consts import *
from ShadowWorld.event import Event


class Entity(object):
    uid_gen = 0

    @classmethod
    def _gen_uid(cls):
        cls.uid_gen += 1
        return cls.uid_gen

    def __init__(self, **kwargs):
        self.__dict__.update(_uid=Entity._gen_uid(), _comps={})

        for key in kwargs:
            self._comps[key] = kwargs[key]

    @property
    def uid(self):
        return self._uid

    def has_comp(self, name):
        return name in self._comps

    def comps(self):
        return dict(self._comps)

    def __getattr__(self, item):
        try:
            return self.__dict__['_comps'][item]
        except KeyError:
            raise AttributeError('Entity component does not exist')

    def __setattr__(self, key, value):
        self._comps[key] = value


class InfoComp:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind


class PlayerComp:
    def __init__(self):
        self.next_loc_dir = [0, 0]
        self.alive = True
        self.death_frame = 0

    def clear(self):
        self.next_loc_dir[0] = 0
        self.next_loc_dir[1] = 0


class PhysComp(object):
    def __init__(self, pos, size):
        self.coll = pygame.Rect(0, 0, size[0], size[1])
        self.pos = pos

        self.vel = (0, 0)
        self.grounded = False
        self.hanging = False

    @property
    def pos(self):
        return self.coll.center

    @pos.setter
    def pos(self, pos):
        self.coll.center = pos


class ControlComp(object):
    def __init__(self, face_right=True, face_up=True, can_climb=False):
        self.face_right = face_right
        self.face_up = face_up
        self.can_climb = can_climb
        self.walk = False
        self.jump = False
        self.climb = False

    @property
    def face_left(self):
        return not self.face_right

    @face_left.setter
    def face_left(self, v):
        self.face_right = not v

    @property
    def face_down(self):
        return not self.face_up

    @face_left.setter
    def face_down(self, v):
        self.face_up = not v

    def clear(self):
        self.walk = False
        self.jump = False
        self.climb = False


class StatsComp:
    def __init__(self, walk_speed=3, jump_strength=7):
        self.walk_speed = walk_speed
        self.jump_strength = jump_strength


class RenderComp:
    def __init__(self, spritesheet, size, layer=0):
        self.spritesheet = spritesheet
        self.size = size
        self.layer = layer


class ThinkComp:
    def __init__(self, behavior):
        self.behavior = behavior


class EffectComp:
    def __init__(self, effects):
        self.effects = effects
        self.triggered = False


def make(**kwargs):
    # print('making', kwargs)
    id = kwargs['id']
    return ENTITY_GEN_MAP[id](**kwargs)


def make_pc(**kwargs):
    print('MAKING PC ---')

    pos = kwargs['pos']
    size = [int(v) for v in kwargs['size'].split()]
    spritesheet = kwargs['spritesheet']
    face_right = True if kwargs['face_right'] in ('True', 'true') else False

    e = Entity(info=InfoComp('You', 'creature'),
               phys=PhysComp(pos=pos, size=size),
               player=PlayerComp(),
               control=ControlComp(face_right, can_climb=True),
               stats=StatsComp(jump_strength=8),
               render=RenderComp(spritesheet, size, 1))
    return e


def make_enemy(**kwargs):
    pos = kwargs['pos']
    size = [int(v) for v in kwargs['size'].split()]
    spritesheet = kwargs['spritesheet']
    face_right = True if kwargs['face_right'] in ('True', 'true') else False
    behavior = kwargs['behavior'].split()

    e = Entity(info=InfoComp('Enemy', 'creature'),
               phys=PhysComp(pos=pos, size=size),
               control=ControlComp(face_right, can_climb=False),
               stats=StatsComp(walk_speed=1),
               render=RenderComp(spritesheet, size, 0),
               thought=ThinkComp(behavior))
    return e


def make_bullet(**kwargs):
    pos = kwargs['pos']
    size = (4, 4)
    spritesheet = 'bullet.png'
    face_right = True if kwargs['face_right'] in ('True', 'true') else False

    e = Entity(info=InfoComp('Bullet', 'bullet'),
               control=ControlComp(face_right, can_climb=False),
               phys=PhysComp(pos=pos, size=size),
               stats=StatsComp(walk_speed=1),
               render=RenderComp(spritesheet, size, 0))
    return e


def make_liquid(**kwargs):
    pos = kwargs['pos']
    size = (TILE_SIZE, TILE_SIZE)
    spritesheet = kwargs['spritesheet']

    e = Entity(info=InfoComp('Liquid', 'liquid'),
               phys=PhysComp(pos=pos, size=size),
               render=RenderComp(spritesheet, size, 2))
    return e


def make_site(**kwargs):
    pos = kwargs['pos']
    size = (TILE_SIZE, TILE_SIZE)
    spritesheet = kwargs['spritesheet']
    effects = kwargs['effects'].split()

    e = Entity(info=InfoComp('Site', 'site'),
               phys=PhysComp(pos=pos, size=size),
               render=RenderComp(spritesheet, size, 0),
               effect=EffectComp(effects))
    return e


def make_site(**kwargs):
    pos = kwargs['pos']
    size = (TILE_SIZE, TILE_SIZE)
    spritesheet = kwargs['spritesheet']
    effects = kwargs['effects'].split()

    e = Entity(info=InfoComp('Site', 'site'),
               phys=PhysComp(pos=pos, size=size),
               render=RenderComp(spritesheet, size, 0),
               effect=EffectComp(effects))
    return e


ENTITY_GEN_MAP = {'player': make_pc,
                  'enemy': make_enemy,
                  'liquid': make_liquid,
                  'site': make_site,
                  'bullet': make_bullet}


def process(gameInstance):
    events = []

    loc = gameInstance.get_current_loc()
    map = loc.map

    for ent in loc.entities:
        info = ent.info

        if info.kind == 'creature':
            try:
                player = ent.player
                phys = ent.phys
                coll = phys.coll

                if not player.alive:
                    continue

                for other_ent in loc.entities:
                    if ent is other_ent:
                        continue

                    if coll.colliderect(other_ent.phys.coll.inflate(-4, -4)):
                        if other_ent.info.kind == 'site':
                            effect = other_ent.effect
                            if not effect.triggered:
                                events.append(Event('site', effects=effect.effects))
                                effect.triggered = True
                        else:
                            player.alive = False
                            events.append(Event('death'))

                            if other_ent.info.kind == 'bullet':
                                events.append(Event('bullet-coll', source_entity=other_ent))

            except AttributeError as err:
                pass

    return events
