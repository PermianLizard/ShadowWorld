import os
import pygame

from ShadowWorld import data, text, image, sound, controller, game, intro
from ShadowWorld.consts import SAVE_FILE

START_GAME_TEXT = None

OPTIONS = None
SELECTED_OPTION = None

FONT = None

COLOR_TITLE = (200, 200, 200)
COLOR_SELECTED = (255, 255, 255)
COLOR_UNSELECTED = (180, 180, 180)
COLOR_UNAVAILABLE = (70, 70, 70)


def enter(**kwargs):
    gen_options()

    global FONT
    FONT = text.get_font('PressStart2P.ttf')

    sound.load_music('menu.ogg')
    sound.play_music()


def exit():
    sound.fadeout_music(100)


def pause():
    sound.fadeout_music(100)


def unpause(**kwargs):
    gen_options()

    sound.load_music('menu.ogg')
    sound.play_music()


def update():
    pass


def draw(surf):
    bg_img = image.get('bg_menu.png')
    surf.blit(bg_img, (0, 0))

    title_surf = FONT.render('SHADOW WORLD', False, COLOR_TITLE)
    title_rect = title_surf.get_rect()
    surf.blit(title_surf, (10, 10))

    top = 50
    for i, option in enumerate(OPTIONS):
        label, available, func = option

        color = COLOR_UNAVAILABLE
        if i == SELECTED_OPTION:
            color = COLOR_SELECTED
        elif available:
            color = COLOR_UNSELECTED

        option_surf = FONT.render(label, False, color)

        surf.blit(option_surf, (20, top))
        top += option_surf.get_rect().height + 5

    top += 20
    for control in ('Run: <LEFT> <RIGHT>', 'Jump: <SPACE>', 'Climb: <UP> <DOWN>'):
        option_surf = FONT.render(control, False, COLOR_TITLE)

        surf.blit(option_surf, (20, top))
        top += option_surf.get_rect().height + 5


def on_key_down(key, mod):
    global SELECTED_OPTION

    if key == pygame.K_ESCAPE:
        controller.pop_scene()

    elif key == pygame.K_UP:
        while True:
            SELECTED_OPTION -= 1
            SELECTED_OPTION %= len(OPTIONS)
            if OPTIONS[SELECTED_OPTION][1]:
                break
        sound.play_sound('select.wav')

    elif key == pygame.K_DOWN:
        while True:
            SELECTED_OPTION += 1
            SELECTED_OPTION %= len(OPTIONS)
            if OPTIONS[SELECTED_OPTION][1]:
                break
        sound.play_sound('select.wav')

    elif key == pygame.K_RETURN:
        OPTIONS[SELECTED_OPTION][2]()


def on_key_up(key, mod):
    pass


def on_mouse_motion(pos, rel, buttons):
    pass


def on_mouse_button_down(pos, button):
    pass


def on_mouse_button_up(pos, button):
    pass


def gen_options():
    global OPTIONS
    OPTIONS = (['Start', True, start],
               ['Load', save_exists(), load],
               ['Quit', True, quit])

    global SELECTED_OPTION
    SELECTED_OPTION = 0


def start():
    controller.push_scene(intro)


def load():
    controller.push_scene(game, load=True)


def quit():
    controller.pop_scene()


def save_exists():
    return os.path.isfile(data.filepath(SAVE_FILE))


if __name__ == '__main__':
    import sys
    import controller

    controller.run(sys.modules[__name__])
