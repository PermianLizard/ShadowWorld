import pygame

from ShadowWorld import image, sound, text
from ShadowWorld.consts import DISPLAY_SIZE, SCREEN_SIZE, FPS, MUSIC_VOLUME


class Quit(Exception):
    pass


SCENE_STACK = None


def top_scene():
    return SCENE_STACK[-1] if SCENE_STACK else None


def push_scene(scene, **kwargs):
    top = top_scene()
    if top:
        top.pause()
    SCENE_STACK.append(scene)
    scene.enter(**kwargs)


def pop_scene(**kwargs):
    popped = None
    if top_scene():
        popped = SCENE_STACK.pop()
        popped.exit()
    top = top_scene()
    if top:
        top.unpause(**kwargs)
    return popped


def swap_scene(scene, **kwargs):
    old = SCENE_STACK.pop() if SCENE_STACK else None
    if old:
        old.exit()
    SCENE_STACK.append(scene)
    scene.enter(**kwargs)
    return old


def run(scene):
    pygame.init()

    display = pygame.display.set_mode(DISPLAY_SIZE)
    screen = pygame.Surface(SCREEN_SIZE).convert()

    clock = pygame.time.Clock()

    global SCENE_STACK
    SCENE_STACK = []

    image.load_images()
    sound.load_sounds()
    text.load_fonts()

    pygame.mixer.music.set_volume(MUSIC_VOLUME)

    push_scene(scene)

    while True:

        top = top_scene()
        if top is None:
            break

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise Quit()
                if event.type == pygame.KEYDOWN:
                    top.on_key_down(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    top.on_key_up(event.key, event.mod)
                elif event.type == pygame.MOUSEMOTION:
                    top.on_mouse_motion(event.pos, event.rel, event.buttons)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    top.on_mouse_button_down(event.pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    top.on_mouse_button_up(event.pos, event.button)

            top.update()
            top.draw(screen)

            pygame.transform.scale(screen, DISPLAY_SIZE, display)

            pygame.display.update()

            clock.tick(FPS)

        except Quit:
            break

    pygame.mixer.music.stop()

    pygame.quit()
