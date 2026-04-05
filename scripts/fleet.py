import pygame

from scripts.alien import Alien


class AlienFleet:
    def __init__(self, game, rows=2, cols=4, start_y=200,
                 spacing_x=15, spacing_y=15, scale=4):
        self.game = game
        self.aliens = []
        self.rows = rows
        self.cols = cols
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y
        self.alien_width = 16 * scale
        self.alien_height = 13 * scale
        self.direction = 1
        self.step = 16
        self.move_timer = pygame.time.get_ticks()
        self.move_delay = 600
        self.min_delay = 100

        cluster_width = cols * self.alien_width + (cols - 1) * spacing_x
        self.start_x = (game.screen_size[0] - cluster_width) // 2
        self.start_y = start_y

        positions = self.grid(
            self.rows,
            self.cols,
            self.alien_width,
            self.alien_height,
            self.spacing_x,
            self.spacing_y,
            self.start_x,
            self.start_y
        )

        for x, y in positions:
            alien = Alien(game.ship, x, y, 'red', 0)
            game.aliens.add(alien)
            self.aliens.append(alien)

    def grid(self, rows, cols, cell_w, cell_h, spacing_x,
                                spacing_y, origin_x, origin_y):
        positions = []
        for row in range(rows):
            for col in range(cols):
                x = origin_x + col * (cell_w + spacing_x)
                y = origin_y + row * (cell_h + spacing_y)
                positions.append((x, y))
        return positions

    def update(self):
        if not self.aliens:
            return

        for alien in self.aliens[:]:
            if not alien.alive():
                self.aliens.remove(alien)
                alien.kill()

        if not self.aliens:
            return

        now = pygame.time.get_ticks()
        if now - self.move_timer >= self.move_delay:
            left = min(alien.rect.left for alien in self.aliens)
            right = max(alien.rect.right for alien in self.aliens)

            if right >= self.game.screen_size[0] or left <= 0:
                self.direction *= -1
                for alien in self.aliens:
                    alien.rect.y += 10

            for alien in self.aliens:
                alien.rect.x += self.direction * self.step
            self.move_timer = now

        alive = len(self.aliens)
        total = self.rows * self.cols
        self.move_delay = max(self.min_delay, int(600 * (alive / total)))

def spawn_fleet(game, phase):
    if game.fleets:
        alive = any(fleet.aliens for fleet in game.fleets)
        if alive:
            return

    if phase == "asteroids":
        clusters = 1
        rows, cols = 4, 8
    elif phase == "quiet":
        clusters = 1
        rows, cols = 6, 12
    elif phase == "boss_fight":
        clusters = 0
        rows, cols = 2, 4
    else:
        return

    for _ in range(clusters):
        fleet = AlienFleet(game, rows=rows, cols=cols, start_y=120)
        game.fleets.append(fleet)

    game.last_alien_spawn = pygame.time.get_ticks()