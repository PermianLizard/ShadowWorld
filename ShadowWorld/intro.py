import pygame

from ShadowWorld import text, image, controller, game

FONT = None

COLOR_TEXT = (200, 200, 200)

LINES = ('Are these memories mine, did I', 'see the day before this one?',
         'This desolate world reflects', 'back my strangeness, my',
         'apart-ness',
         'My creators gave me this mind', 'yet I do not know why.',
         'They are still here', 'I must find them ...',
         '',
         '<ENTER>')


def enter(**kwargs):
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

    top = 10
    for line in LINES:
        line_surf = FONT.render(line, False, COLOR_TEXT)

        surf.blit(line_surf, (10, top))
        top += line_surf.get_rect().height + 5


def on_key_down(key, mod):
    if key == pygame.K_ESCAPE:
        controller.pop_scene()
    elif key == pygame.K_RETURN:
        controller.swap_scene(game)


def on_key_up(key, mod):
    pass


def on_mouse_motion(pos, rel, buttons):
    pass


def on_mouse_button_down(pos, button):
    pass


def on_mouse_button_up(pos, button):
    pass


if __name__ == '__main__':
    import sys
    import controller

    controller.run(sys.modules[__name__])
