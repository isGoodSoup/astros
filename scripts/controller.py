import pygame
from scripts.shared import joysticks, controller

def update_controller(game, screen_size, dt):
    if joysticks:
        game.cursor_pos[0] += game.motion[0] * game.cursor_speed * dt
        game.cursor_pos[1] += game.motion[1] * game.cursor_speed * dt

        game.cursor_pos[0] = max(0, min(screen_size[0], game.cursor_pos[0]))
        game.cursor_pos[1] = max(0, min(screen_size[1], game.cursor_pos[1]))

        now = pygame.time.get_ticks()

        axis_x = controller.get_axis(0)
        axis_y = controller.get_axis(1)