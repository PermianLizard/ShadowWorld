import pygame

from ShadowWorld import text, image, controller

FONT = None

COLOR_TEXT = (200, 200, 200)

LINES = ('Life recedes, the world fades.', 'And yet I am freed.',
         'This existence is only a flash', 'in an indescribable void.',
         'Non being is what we secretly', 'look for.',
         'For it is the only true bliss', 'that there really is',
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
    if key in (pygame.K_RETURN, pygame.K_ESCAPE):
        controller.pop_scene()


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
