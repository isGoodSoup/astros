import math

import pygame
from pygame.constants import *

lock_y = False

def get_next_skill(current, skills, direction):
    if not skills:
        return None

    if current is None:
        return skills[0]

    cx, cy = current.pos
    dir_x, dir_y = direction

    candidates = []

    for skill in skills:
        if skill == current:
            continue

        sx, sy = skill.pos
        dx = sx - cx
        dy = sy - cy

        if dir_x != 0 and (dx * dir_x) <= 0:
            continue
        if dir_y != 0 and (dy * dir_y) <= 0:
            continue

        dist = dx * dx + dy * dy
        candidates.append((dist, skill))

    if not candidates:
        return current

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]

def update_movement(game, delta, screen_size):
    key_pressed = pygame.key.get_pressed()

    movement_x = 0
    movement_y = 0

    if key_pressed[K_LEFT]:
        movement_x -= game.ship.velocity * delta * 60

    if key_pressed[K_RIGHT]:
        movement_x += game.ship.velocity * delta * 60

    if not lock_y:
        if key_pressed[K_UP]:
            movement_y -= game.ship.velocity * delta * 60

        if key_pressed[K_DOWN]:
            movement_y += game.ship.velocity * delta * 60

    movement_x += game.input.left_joystick[0] * game.ship.velocity * delta * 60
    if not lock_y:
        movement_y += game.input.left_joystick[1] * game.ship.velocity * delta * 60

    game.ship_x = max(0, min(screen_size[0] - game.base.get_width(),
                             game.ship_x + movement_x))
    game.ship_y = max(0, min(screen_size[1] - game.base.get_height(),
                             game.ship_y + movement_y))

    if movement_x < 0:
        game.ship.direction = "left"
    elif movement_x > 0:
        game.ship.direction = "right"
    else:
        game.ship.direction = "idle"
    game.ship.moving = movement_x != 0 or movement_y != 0

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
            game.mode = "mouse"
            game.input.last_input_time = pygame.time.get_ticks()
        game.last_cursor_pos = mouse_pos

        if abs(game.input.right_joystick[0]) > 0.05 or abs(game.input.right_joystick[1]) > 0.05:
            game.input.mode = "controller"
            game.input.last_input_time = pygame.time.get_ticks()

        if game.input.mode == "mouse":
            game.input.cursor_pos = list(mouse_pos)
        elif game.input.mode == "controller":
            game.input.cursor_pos[0] += game.input.right_joystick[0] * cursor_speed
            game.input.cursor_pos[1] += game.input.right_joystick[1] * cursor_speed
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

def update_ship_angle(game):
    cx, cy = game.ship.rect.center
    mx, my = game.input.cursor_pos
    dx = mx - cx
    dy = my - cy
    angle_rad = math.atan2(-dy, dx)
    target_angle = math.degrees(angle_rad)
    game.ship.rotate_to(target_angle, smooth=False)