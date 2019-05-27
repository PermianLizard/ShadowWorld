import pygame

from ShadowWorld import text, image, sound, controller

START_GAME_TEXT = None

OPTIONS = None
SELECTED_OPTION = None

FONT = None

COLOR_SELECTED = (255, 255, 255)
COLOR_UNSELECTED = (180, 180, 180)


def enter(**kwargs):
    global OPTIONS
    OPTIONS = (['Resume', resume],
               ['Quit', quit])

    global SELECTED_OPTION
    SELECTED_OPTION = 0

    global FONT
    FONT = text.get_font('PressStart2P.ttf')


def exit():
    pass


def pause():
    pass


def unpause(**kwargs):
    pass


def update():
    pass


def draw(surf):
    bg_img = image.get('bg_menu.png')
    surf.blit(bg_img, (0, 0))

    top = 30
    for i, option in enumerate(OPTIONS):
        label, func = option

        color = COLOR_UNSELECTED
        if i == SELECTED_OPTION:
            color = COLOR_SELECTED

        txt_surf = FONT.render(label, False, color)

        surf.blit(txt_surf, (30, top))
        top += txt_surf.get_rect().height + 5


def on_key_down(key, mod):
    global SELECTED_OPTION

    if key == pygame.K_ESCAPE:
        resume()

    elif key == pygame.K_UP:
        SELECTED_OPTION -= 1
        SELECTED_OPTION %= len(OPTIONS)
        sound.play_sound('select.wav')

    elif key == pygame.K_DOWN:
        SELECTED_OPTION += 1
        SELECTED_OPTION %= len(OPTIONS)
        sound.play_sound('select.wav')

    elif key == pygame.K_RETURN:
        OPTIONS[SELECTED_OPTION][1]()


def on_key_up(key, mod):
    pass


def on_mouse_motion(pos, rel, buttons):
    pass


def on_mouse_button_down(pos, button):
    pass


def on_mouse_button_up(pos, button):
    pass


def resume():
    controller.pop_scene()


def quit():
    controller.pop_scene()
    controller.pop_scene()


if __name__ == '__main__':
    import sys
    import controller

    controller.run(sys.modules[__name__])
