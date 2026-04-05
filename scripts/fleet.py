import pygame
from scripts.alien import Alien

def alien_formation(game, formation="line", base_x=None, base_y=None):
    aliens_to_spawn = game.alien_spawn_count
    alien_width = 26 * 4
    alien_height = 32 * 4
    spacing_x = 10
    spacing_y = 50
    limit = pygame.display.Info().current_h // 4

    if base_x is None:
        if formation == "line":
            base_x = game.ship_x - ((aliens_to_spawn - 1) * (alien_width + spacing_x)) // 2
        elif formation == "block":
            cols = 3
            base_x = game.ship_x - ((cols - 1) * (alien_width + spacing_x)) // 2
        elif formation == "clutch":
            base_x = game.ship_x

    if base_y is None:
        base_y = limit

    positions = []

    if formation == "line":
        for i in range(aliens_to_spawn):
            positions.append((base_x + i * (alien_width + spacing_x), base_y))

    elif formation == "block":
        cols = 3
        for i in range(aliens_to_spawn):
            r = i // cols
            c = i % cols
            positions.append((base_x + c * (alien_width + spacing_x),
                              base_y + r * (alien_height + spacing_y)))

    elif formation == "clutch":
        mid = aliens_to_spawn // 2
        for i in range(aliens_to_spawn):
            offset = (i - mid) * (alien_width + spacing_x)
            positions.append((base_x + offset, base_y + abs(i - mid) * 20))

    for pos in positions:
        new_alien = Alien(game.ship, x=pos[0], y=-150,
            frame=2, offset_x=pos[0] - game.ship.rect.centerx, offset_y=pos[1])
        game.aliens.add(new_alien)