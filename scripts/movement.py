import math
import pygame

from pygame.locals import K_w, K_a, K_s, K_d
from scripts.constants import FPS, MAX_PITCH


def update_movement(game, delta, screen_size):
    ship = game.ship
    ship.angle_pitch = max(-MAX_PITCH, min(MAX_PITCH, ship.angle_pitch))

    lx, ly = game.input.left_joystick

    length = math.hypot(lx, ly)
    if length > 1:
        lx /= length
        ly /= length

    yaw = ship.angle_yaw

    forward_x = math.cos(yaw)
    forward_y = math.sin(yaw)

    right_x = -forward_y
    right_y = forward_x

    kx = 0
    ky = 0

    keys = pygame.key.get_pressed()

    if keys[K_w]:
        ky += 1
    if keys[K_s]:
        ky -= 1
    if keys[K_d]:
        kx += 1
    if keys[K_a]:
        kx -= 1

    move_x = kx + lx
    move_y = ky - ly  # joystick Y is usually inverted

    world_x = (right_x * move_x) + (forward_x * move_y)
    world_y = (right_y * move_x) + (forward_y * move_y)

    movement = pygame.Vector2(world_x, world_y)

    if movement.length_squared() > 0:
        movement = movement.normalize()

    speed = ship.velocity * delta * FPS

    ship.wx += movement.x * speed
    ship.wy += movement.y * speed

    ship.moving = (move_x != 0)

    if ship.moving:
        if ship.tower_boost_applied:
            ship.shield -= ship.tower_boost
            ship.tower_boost = 0
            ship.tower_boost_applied = False
    else:
        ship.shield += ship.tower_boost
        ship.tower_boost_applied = True