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
        if not game.ship.moving:
            for skill in game.skills.skills:
                if skill.name == "Tower" and skill.unlocked:
                    skill.ability.apply(game.ship, skill.level)

    if key_pressed[K_SPACE]:
        current_time = pygame.time.get_ticks()
        if current_time - game.last_shot_time >= game.ship.shot_cooldown:
            new_projectiles = game.ship.shoot(game.base, game.last_shot_time,
                                              game.ship.shot_cooldown,
                                              game.play_sound, game.sounds)
            game.projectiles.add(new_projectiles)
            game.last_shot_time = current_time