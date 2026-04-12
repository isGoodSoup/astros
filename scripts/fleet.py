import random

import pygame

from scripts.settings import (ASTEROID_PHASES, ALIEN_PHASES, SCALE,
                              ALIEN_FORMATION, ONE_SECOND, ALIEN_MOVES)


class AlienFleet:
    def __init__(self, game, rows=2, cols=4, start_y=200,
                 spacing_x=15, spacing_y=15, scale=SCALE,
                 movement_type="sideways"):
        self.game = game
        self.formation = random.choice(ALIEN_FORMATION)
        self.movement_type = movement_type
        self.rows = rows
        self.cols = cols
        self.aliens = pygame.sprite.Group()
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y
        self.alien_width = 16 * scale
        self.alien_height = 11 * scale

        self.direction = 1
        self.step = 10

        self.velocity = pygame.math.Vector2(random.uniform(-2, 2),
            random.uniform(-2, 2))
        self.max_speed = 2.5
        self.phase2_change_interval = ONE_SECOND
        self.phase2_change_time = pygame.time.get_ticks()

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
        # Remove dead aliens
        for a in list(self.aliens):
            if not a.alive():
                self.aliens.remove(a)

        if len(self.aliens) == 0:
            return

        if self.movement_type == "sideways":
            self._update_classic()
        elif self.movement_type == "chaotic":
            self._update_chaos()

        for alien in self.aliens:
            alien.update()

    def alive(self):
        return any(a.alive() for a in self.aliens)

    def _update_classic(self):
        left = min(a.rect.left for a in self.aliens.sprites())
        right = max(a.rect.right for a in self.aliens.sprites())

        if right >= self.game.screen_size[0] or left <= 0:
            self.direction *= -1
            for alien in self.aliens:
                alien.rect.y += 10

        for alien in self.aliens:
            alien.rect.x += self.direction * self.step

    def _update_chaos(self):
        now = pygame.time.get_ticks()
        screen_width, screen_height = self.game.screen_size

        if now - self.phase2_change_time > self.phase2_change_interval:
            self.velocity.x += random.uniform(-2, 2)
            self.velocity.y += random.uniform(-2, 2)

            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)

            self.phase2_change_time = now

        dx = int(self.velocity.x)
        dy = int(self.velocity.y)

        for alien in self.aliens:
            alien.rect.x += dx
            alien.rect.y += dy

        left = min(a.rect.left for a in self.aliens)
        right = max(a.rect.right for a in self.aliens)
        top = min(a.rect.top for a in self.aliens)
        bottom = max(a.rect.bottom for a in self.aliens)

        if left <= 0 or right >= screen_width:
            self.velocity.x *= -1
            correction = -left if left <= 0 else screen_width - right
            for alien in self.aliens:
                alien.rect.x += correction

        if top <= 0 or bottom >= screen_height:
            self.velocity.y *= -1
            correction = -top if top <= 0 else screen_height - bottom
            for alien in self.aliens:
                alien.rect.y += correction

def new_fleet_block(game):
    max_cols = max(1,(game.screen_size[0] + 15) // (16 * SCALE + 15))
    rows = random.randint(4, 9)
    cols = random.randint(4, min(12, max_cols))
    return rows, cols

def spawn_fleet(game, phase_index):
    for fleet in list(game.sprites.fleets):
        for alien in list(fleet.aliens):
            alien.kill()
        game.sprites.fleets.remove(fleet)

    if phase_index in ASTEROID_PHASES:
        movement_type = "sideways"
    elif phase_index in ALIEN_PHASES:
        movement_type = random.choice(ALIEN_MOVES)
    elif phase_index == len(game.state.phases) - 1:
        movement_type = "chaotic"
    else:
        return

    rows, cols = new_fleet_block(game)

    fleet = AlienFleet(game, rows=rows, cols=cols,
        start_y=120, movement_type=movement_type)
    game.sprites.fleets.append(fleet)

    for alien in fleet.aliens:
        game.sprites.aliens.add(alien)

    game.spawns.last_alien_spawn = pygame.time.get_ticks()