import random

import pygame

from scripts.objects.celestial import BlackHole
from scripts.objects.explode import Explosion
from scripts.system.constants import (HIGH_RUMBLE_MS, SHOCKWAVE_SPEED, SHOCKWAVE_RADIUS, \
                              SCREEN_SHAKE, ALIEN_SHOT_TIMER_MS, CROSSHAIRS)
from scripts.engine.shared import joysticks, controller
from scripts.objects.shockwave import Shockwave

class Events:
    def __init__(self):
        self.ALIENLASER = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ALIENLASER, ALIEN_SHOT_TIMER_MS)

        self.MUSIC_END = pygame.USEREVENT + 2
        pygame.mixer.music.set_endevent(self.MUSIC_END)

    def alien_shoot_event(self, game):
        if pygame.time.get_ticks() < game.sprites.alien_delay:
            return

        shots_this_frame = 0
        if random.random() > 0.5:
            shooters = random.sample(game.sprites.aliens.sprites(),
                                     k=min(1, len(game.sprites.aliens)))
        else:
            shooters = [alien for alien in game.sprites.aliens.sprites()
                        if abs(alien.rect.centerx -
                               game.ship.rect.centerx) <= CROSSHAIRS]

        for alien in shooters:
            new_projectiles = alien.shoot(game.ship,
                                          alien.shot_cooldown)
            if new_projectiles:
                shots_this_frame += len(new_projectiles)
                game.sprites.enemy_projectiles.add(*new_projectiles)

        if shots_this_frame > 0 and game.state.play_sound:
            game.mixer.play(0)

    def nuke_event(self, center, game):
        game.sprites.shockwaves.append(Shockwave(center, max_radius=SHOCKWAVE_RADIUS,
                                         speed=SHOCKWAVE_SPEED))
        game.sprites.explosions.add(Explosion(center[0], center[1],
                                      game.sprites.frame_big_explode))

        if game.state.can_screen_shake:
            game.screen_shake = SCREEN_SHAKE + 5
            if joysticks and game.state.can_rumble:
                controller.rumble(1, 1, HIGH_RUMBLE_MS)

    def torpedo_event(self, center, radius, game):
        game.sprites.shockwaves.append(Shockwave(center, max_radius=radius,
                                         speed=SHOCKWAVE_SPEED // 2))
        game.sprites.explosions.add(Explosion(center[0], center[1],
                                      game.sprites.frame_explode))

        if game.state.can_screen_shake:
            game.screen_shake = SCREEN_SHAKE // 2
            if joysticks and game.state.can_rumble:
                controller.rumble(0.5, 0.5, HIGH_RUMBLE_MS // 2)

    def black_hole_event(self, game):
        x = random.randint(100, game.screen_size[0] - 100)
        y = -200
        game.sprites.celestials.add(BlackHole(game, x, y))