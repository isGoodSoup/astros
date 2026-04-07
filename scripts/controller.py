import pygame
from scripts.shared import joysticks, controller

def update_controller(game, screen_size, dt):
    if joysticks:
        axis_x = controller.get_axis(2)
        axis_y = controller.get_axis(3)

        deadzone = 0.2
        axis_x = axis_x if abs(axis_x) > deadzone else 0
        axis_y = axis_y if abs(axis_y) > deadzone else 0

        game.cursor_pos[0] += axis_x * game.cursor_speed * dt
        game.cursor_pos[1] += axis_y * game.cursor_speed * dt

        game.cursor_pos[0] = max(0, min(screen_size[0], game.cursor_pos[0]))
        game.cursor_pos[1] = max(0, min(screen_size[1], game.cursor_pos[1]))

        if axis_x != 0 or axis_y != 0:
            game.cursor_visible = True
            game.last_move_time = pygame.time.get_ticks()