import pygame

from scripts.system.constants import INPUT_CONTROLLER
from scripts.engine.shared import joysticks, controller
from scripts.engine.utils import apply_curve

def update_controller(game, screen_size, delta):
    if not joysticks:
        return

    lx = controller.get_axis(0)
    ly = controller.get_axis(1)
    lx = 0 if abs(lx) < game.input.deadzone else lx
    ly = 0 if abs(ly) < game.input.deadzone else ly

    game.input.left_joystick[0] = lx
    game.input.left_joystick[1] = ly

    game.ship.rect.x += int(lx * game.ship.velocity * delta)
    game.ship.rect.y += int(ly * game.ship.velocity * delta)
    game.ship.hitbox.center = game.ship.rect.center

    rx = controller.get_axis(2)
    ry = controller.get_axis(3)
    rx = 0 if abs(rx) < game.input.deadzone else rx
    ry = 0 if abs(ry) < game.input.deadzone else ry

    rx = apply_curve(game, rx)
    ry = apply_curve(game, ry)

    if lx != 0 or ly != 0:
        game.input.mode = INPUT_CONTROLLER

    if rx != 0 or ry != 0:
        game.input.mode = INPUT_CONTROLLER
        if game.input.moving_hud:
            return

        game.input.cursor_pos[0] += rx * game.input.cursor_speed * delta
        game.input.cursor_pos[1] += ry * game.input.cursor_speed * delta

        game.input.cursor_pos[0] = max(0, min(screen_size[0], game.input.cursor_pos[0]))
        game.input.cursor_pos[1] = max(0, min(screen_size[1], game.input.cursor_pos[1]))

        game.input.cursor_visible = True
        game.input.last_move_time = pygame.time.get_ticks()