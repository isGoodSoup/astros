import random

import pygame

from scripts.alien import Alien
from scripts.settings import (ASTEROID_PHASES, ALIEN_PHASES, SCALE,
                              ALIEN_FORMATION)


class AlienFleet:
    def __init__(self, game, rows=2, cols=4, start_y=200,
                 spacing_x=15, spacing_y=15, scale=SCALE):
        self.game = game
        self.formation = random.choice(ALIEN_FORMATION)
        self.rows = rows
        self.cols = cols
        self.aliens = pygame.sprite.Group()
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y
        self.alien_width = 16 * scale
        self.alien_height = 11 * scale
        self.direction = 1

        self.step = 10
        self.move_timer = pygame.time.get_ticks()

        cluster_width = cols * self.alien_width + (cols - 1) * spacing_x
        self.start_x = (game.screen_size[0] - cluster_width) // 2
        self.start_y = start_y

        positions = self.grid(self.rows, self.cols, self.alien_width,
            self.alien_height, self.spacing_x, self.spacing_y, self.start_x,
                              self.start_y)

        if game.spawns.shuffle_enemies:
            random.shuffle(positions)

        for x, y in positions:
            color = game.state.phase_colors[game.state.phase_index %
                                            len(game.state.phase_colors)]
            alien = Alien(game, game.ship, x, y, color, 0, game.screen)
            self.aliens.add(alien) # type: ignore
            game.sprites.aliens.add(alien)

    def grid(self, rows, cols, cell_w, cell_h, spacing_x,
                                spacing_y, origin_x, origin_y):
        positions = []
        if self.formation == "block":
            for row in range(rows):
                for col in range(cols):
                    x = origin_x + col * (cell_w + spacing_x)
                    y = origin_y + row * (cell_h + spacing_y)
                    positions.append((x, y))

        elif self.formation == "line":
            count = rows * cols
            for i in range(count):
                x = origin_x + i * (cell_w + spacing_x)
                y = origin_y
                positions.append((x, y))

        elif self.formation == "clutch":
            for row in range(rows):
                for col in range(cols):
                    x = origin_x + col * (cell_w + spacing_x)
                    if row % 2 == 1:
                        x += cell_w // 2
                    y = origin_y + row * (cell_h + spacing_y)
                    positions.append((x, y))
        return positions

    def update(self):
        for a in list(self.aliens):
            if not a.alive():
                self.aliens.remove(a)

        if len(self.aliens) == 0:
            return

        left = min(a.rect.left for a in self.aliens.sprites())
        right = max(a.rect.right for a in self.aliens.sprites())

        if right >= self.game.screen_size[0] or left <= 0:
            self.direction *= -1
            for alien in list(self.aliens):
                alien.rect.y += 10

        for alien in list(self.aliens):
            alien.rect.x += self.direction * self.step
            alien.update()

    def alive(self):
        return any(a.alive() for a in self.aliens)

def new_fleet_block():
    return [random.randint(1, 9), random.randint(1, 6)]

def spawn_fleet(game, phase):
    for fleet in list(game.sprites.fleets):
        for alien in fleet.aliens:
            if alien in game.sprites.entities:
                game.sprites.entities.remove(alien)
            if alien in game.sprites.aliens:
                game.sprites.aliens.remove(alien)
        game.sprites.fleets.remove(fleet)

    if phase in ASTEROID_PHASES:
        clusters = 1
        rows, cols = new_fleet_block()
    elif phase in ALIEN_PHASES:
        clusters = 1
        rows, cols = new_fleet_block()
    elif phase == game.state.phases[-1]:
        clusters = 1
        rows, cols = new_fleet_block()
    else:
        return

    for _ in range(clusters):
        fleet = AlienFleet(game, rows=rows, cols=cols, start_y=120)
        game.sprites.fleets.append(fleet)
        for alien in fleet.aliens:
            game.sprites.entities.add(alien)
            game.sprites.aliens.add(alien)
    game.spawns.last_alien_spawn = pygame.time.get_ticks()