import random

import pygame
from scripts.alien import Alien

class AlienFleet:
    def __init__(self, game, rows=2, cols=4, start_y=200,
                 spacing_x=5, spacing_y=5, scale=3):
        self.game = game
        self.aliens = []
        self.rows = rows
        self.cols = cols
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y
        self.alien_width = 16 * scale
        self.alien_height = 13 * scale
        self.direction = 1
        self.speed = 1
        self.move_timer = pygame.time.get_ticks()
        self.move_delay = 50

        cluster_width = cols * self.alien_width + (cols - 1) * spacing_x
        self.start_x = (game.screen_size[0] - cluster_width) // 2
        self.start_y = start_y

        for row in range(rows):
            for col in range(cols):
                x = self.start_x + col * (self.alien_width + spacing_x)
                y = self.start_y + row * (self.alien_height + spacing_y)
                new_alien = Alien(game.ship, x, y, 'red', 0)
                game.aliens.add(new_alien)
                self.aliens.append(new_alien)

        self.left_edge = self.start_x
        self.right_edge = self.start_x + cluster_width

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.move_timer >= self.move_delay:
            self.left_edge += self.direction * self.speed
            self.right_edge += self.direction * self.speed

            if self.right_edge >= self.game.screen_size[0] or self.left_edge <= 0:
                self.direction *= -1
                self.left_edge += self.direction * self.speed
                self.right_edge += self.direction * self.speed
                for alien in self.aliens:
                    alien.pos.y += 10
                    alien.rect.y = int(alien.pos.y)

            for alien in self.aliens:
                alien.pos.x += self.direction * self.speed
                alien.rect.x = int(alien.pos.x)

            self.move_timer = now

def spawn_phase_aliens(game, phase):
    now = pygame.time.get_ticks()
    if now - game.last_alien_spawn < game.alien_spawn_interval:
        return

    if phase == "asteroids":
        clusters = random.randint(1, 3)
        for _ in range(clusters):
            AlienFleet(game, rows=3, cols=8, start_y=80)

    elif phase == "quiet":
        clusters = random.randint(1, 2)
        for _ in range(clusters):
            AlienFleet(game, rows=3, cols=6, start_y=100)

    elif phase == "boss_fight":
        clusters = random.randint(0, 2)
        for _ in range(clusters):
            AlienFleet(game, rows=2, cols=4, start_y=120)

    game.last_alien_spawn = now