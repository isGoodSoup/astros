import pygame
from pygame.constants import *

lock_y = False

def update_movement(game, delta, screen_size):
    key_pressed = pygame.key.get_pressed()
    joy_x = game.joy_axis[0]

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

    movement_x += joy_x * game.ship.velocity * delta * 60
    if not lock_y:
        movement_y += game.joy_axis[1] * game.ship.velocity * delta * 60

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
    elif not game.ship.moving:
        if game.skill_tab.active:
            cursor_speed = game.cursor_speed * delta
            game.cursor_pos[0] += game.joy_axis[0] * cursor_speed
            game.cursor_pos[1] += game.joy_axis[1] * cursor_speed

            game.cursor_pos[0] = max(0, min(screen_size[0], game.cursor_pos[0]))
            game.cursor_pos[1] = max(0, min(screen_size[1], game.cursor_pos[1]))

            if game.current_phase_options:
                closest_skill = None
                min_dist = float('inf')
                for skill in game.current_phase_options:
                    dx = game.cursor_pos[0] - skill.pos[0]
                    dy = game.cursor_pos[1] - skill.pos[1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_skill = skill
                game.selected_skill = closest_skill

                for skill in game.current_phase_options:
                    skill.hovered = (skill == game.selected_skill)

    if key_pressed[K_SPACE]:
        current_time = pygame.time.get_ticks()
        if current_time - game.last_shot_time >= game.ship.shot_cooldown:
            new_projectiles = game.ship.shoot(gun_type=game.ship.gun)
            game.projectiles.add(*new_projectiles)
            game.last_shot_time = current_time

            if game.ship.gun == "shotgun":
                game.screen_shake = 20