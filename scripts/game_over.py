import pygame

from scripts.ship import Ship
from scripts.utils import center

def game_lost(game, font, screen, screen_size):
    now = pygame.time.get_ticks()
    if now - game.last_blink > 500:
        game.count += 1
        game.last_blink = now

    colors = ["RED", (0, 0, 0, 0)]
    game_over = font.render("GAME OVER", True, colors[game.count % 2])

    if game.state.play_sound and getattr(game, "game_over_fx", True):
        game.sounds[-1].play()
        game.state.game_over_fx = False

    if game.state.score > game.state.high_score:
        game.state.high_score = game.state.score
        game.save_config()

    score_text = font.render(f"{int(game.state.score):05}", True, "WHITE")
    stopwatch = game.stopwatch if game.stopwatch is not None else (
        font.render("00:00:00", True, "WHITE"))
    game_over_x = center(game, game_over, screen_size)
    game_over_y = screen_size[1] // 2
    screen.blit(game_over, [game_over_x, game_over_y])
    screen.blit(score_text, [center(game, score_text, screen_size), game_over_y + 25])
    screen.blit(stopwatch, [center(game, stopwatch, screen_size), game_over_y + 50])


def reboot(game, screen_size):
    saved_stats = game.ship.get_stats()

    game.projectiles.empty()
    game.enemy_projectiles.empty()
    game.entities.empty()
    game.aliens.empty()
    game.fleets.clear()
    game.explosions.empty()
    game.upgrades.empty()
    game.floating_numbers.empty()
    game.particles.clear()

    framew = game.ship_sprite[0].sheet.get_width() // game.ship_frames
    frameh = game.ship_sprite[0].sheet.get_height()
    game.ship = Ship(game.ship_sprite[0], 0, 0, game.frame, framew, frameh,
                     columns=game.ship_frames)

    for attr, value in saved_stats.items():
        setattr(game.ship, attr, value)

    game.spawnpoint(game.ship, screen_size, game.ship_sprite, game.ship_frames)

    game.ship_alive = True
    game.ship.hitpoints = game.ship.max_hitpoints
    game.ship.shield = game.ship.max_shield
    game.ship.ammo = game.ship.base_ammo
    game.ship.charges = game.ship.base_charges

    game.frame = 0
    game.last_update = pygame.time.get_ticks()
    game.last_asteroid_spawn = 0
    game.last_shot_time = 0
    game.state.score = 0
    game.clock.hours = game.clock.minutes\
        = game.clock.seconds = game.clock.milliseconds = 0
    game.clock.stopwatch = None
    game.state.current_phase = game.state.phases[0]
    game.state.phase_index = 0
    game.state.phase_start_time = pygame.time.get_ticks()
    game.state.phase_ending = False
    game.state.game_over = False
    game.state.game_over_fx = True

    if game.state.play_sound:
        pygame.mixer.music.play(-1)