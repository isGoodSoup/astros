import pygame
from pygame.constants import *

from scripts.constants import (FPS, INPUT_MOUSE, INPUT_CONTROLLER)

lock_y = False


def update_movement(game, delta, screen_size):
    key_pressed = pygame.key.get_pressed()

    ACCEL = game.ship.velocity * 6.0
    MAX_SPEED = game.ship.velocity
    DRAG = 0.78

    if not hasattr(game.ship, "vel_x"):
        game.ship.vel_x = 0.0
        game.ship.vel_y = 0.0

    ix = 0.0
    iy = 0.0

    if key_pressed[K_LEFT] or key_pressed[K_a]:
        ix -= 1
    if key_pressed[K_RIGHT] or key_pressed[K_d]:
        ix += 1

    if not lock_y:
        if key_pressed[K_UP] or key_pressed[K_w]:
            iy -= 1
        if key_pressed[K_DOWN] or key_pressed[K_s]:
            iy += 1

    ix += game.input.left_joystick[0]
    if not lock_y:
        iy += game.input.left_joystick[1]

    length = (ix * ix + iy * iy) ** 0.5
    if length > 1e-6:
        ix /= length
        iy /= length

    game.ship.vel_x += ix * ACCEL * delta * FPS
    game.ship.vel_y += iy * ACCEL * delta * FPS

    speed = (game.ship.vel_x ** 2 + game.ship.vel_y ** 2) ** 0.5
    accel_mag = (ix * ix + iy * iy) ** 0.5

    if accel_mag > 0:
        emit_count = 1 + int(accel_mag * 3)

        for _ in range(emit_count):
            game.sprites.spawn_thruster_particle(game.ship)

    if speed > MAX_SPEED:
        scale = MAX_SPEED / speed
        game.ship.vel_x *= scale
        game.ship.vel_y *= scale

    game.ship.vel_x *= DRAG
    game.ship.vel_y *= DRAG

    game.ship.rect.x += game.ship.vel_x * delta * FPS
    game.ship.rect.y += game.ship.vel_y * delta * FPS

    game.ship.rect.x = max(0, min(
            screen_size[0] - game.sprites.base.get_width(),
            game.ship.rect.x))
    game.ship.rect.y = max(0, min(
            screen_size[1] - game.sprites.base.get_height(),
            game.ship.rect.y))

    if game.ship.vel_x < -0.1:
        game.ship.direction = "left"
    elif game.ship.vel_x > 0.1:
        game.ship.direction = "right"
    else:
        game.ship.direction = "idle"

    game.ship.moving = (game.ship.vel_x != 0 or game.ship.vel_y != 0)

    if game.ship.moving:
        if game.ship.tower_boost_applied:
            game.ship.shield -= game.ship.tower_boost
            game.ship.tower_boost = 0
            game.ship.tower_boost_applied = False
    else:
        game.ship.shield += game.ship.tower_boost
        game.ship.tower_boost_applied = True

    if game.hud.skill_tab.active:
        cursor_speed = game.input.cursor_speed * delta

        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos != getattr(game, "last_cursor_pos", (0, 0)):
            game.mode = INPUT_MOUSE
            game.input.last_input_time = pygame.time.get_ticks()
        game.last_cursor_pos = mouse_pos

        if abs(game.input.right_joystick[0]) > 0.05 or abs(
                game.input.right_joystick[1]) > 0.05:
            game.input.mode = INPUT_CONTROLLER
            game.input.last_input_time = pygame.time.get_ticks()

        if game.input.mode == INPUT_MOUSE:
            game.input.cursor_pos = list(mouse_pos)

        elif game.input.mode == INPUT_CONTROLLER:
            game.input.cursor_pos[0] += game.input.right_joystick[
                                            0] * cursor_speed
            game.input.cursor_pos[1] += game.input.right_joystick[
                                            1] * cursor_speed

            game.input.cursor_pos[0] = max(0, min(game.screen_size[0],
                                                  game.input.cursor_pos[0]))
            game.input.cursor_pos[1] = max(0, min(game.screen_size[1],
                                                  game.input.cursor_pos[1]))

        current_time = pygame.time.get_ticks()

        dx, dy = game.input.right_joystick
        threshold = 0.5

        if current_time - game.input.last_nav_time > game.input.nav_cooldown:
            direction = None

            if abs(dx) > abs(dy):
                if dx > threshold:
                    direction = (1, 0)
                elif dx < -threshold:
                    direction = (-1, 0)
            else:
                if dy > threshold:
                    direction = (0, 1)
                elif dy < -threshold:
                    direction = (0, -1)

            if direction:
                game.input.selected_skill = get_next_skill(
                    game.input.selected_skill,
                    game.state.current_phase_options,
                    direction
                )
                game.input.last_nav_time = current_time

        closest_skill = None
        min_dist = float('inf')

        for skill in game.current_phase_options:
            dx = game.input.cursor_pos[0] - skill.pos[0]
            dy = game.input.cursor_pos[1] - skill.pos[1]
            dist = dx * dx + dy * dy

            if dist < min_dist:
                min_dist = dist
                closest_skill = skill

        game.input.selected_skill = closest_skill

        for skill in game.state.current_phase_options:
            skill.hovered = (skill == game.input.selected_skill)
