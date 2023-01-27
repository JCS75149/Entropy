import pygame



pygame.font.init()
font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x1, y1, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = x1, y1
    surf.blit(text_surface, text_rect)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen_size = 1500, 750

WIDTH = screen_size[0]
HEIGHT = screen_size[1]
FPS = 60


def pause():
    keep_looping = True
    while keep_looping:
        for event1 in pygame.event.get():
            if event1.type == pygame.KEYDOWN:
                # if event1.key == pygame.K_z:
                keep_looping = False


def convert(pos):
    x1 = pos[0]
    y1 = screen_size[1]-pos[1]
    c_pos = x1, y1
    return c_pos
