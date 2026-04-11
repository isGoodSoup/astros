import pygame

from scripts.lang import local
from scripts.settings import ONE_SECOND, COLOR_WHITE, COLOR_RED, PHASE_ACTIVE
from scripts.ship import Ship
from scripts.utils import center

def game_lost(game, font, screen, screen_size):
    now = pygame.time.get_ticks()
    if now - game.last_blink > ONE_SECOND//2:
        game.last_blink = now

    game_over = font.render(local.t('game.defeat'), True, COLOR_RED)

    if game.state.play_sound and getattr(game, "game_over_fx", True):
        game.sounds[-1].play()
        game.state.game_over_fx = False

    if game.state.score > game.state.high_score:
        game.state.high_score = game.state.score
        game.save_config()

    game.clock.milliseconds = 0
    game.clock.seconds = 0
    game.clock.minutes = 0
    game.clock.hours = 0

    score_text = font.render(f"{int(game.state.score):05}", True, COLOR_WHITE)
    stopwatch = game.clock.stopwatch if game.clock.stopwatch is not None else \
        (font.render("00:00:00", True, COLOR_WHITE))
    game_over_x = center(game, game_over, screen_size)
    game_over_y = screen_size[1] // 2

    if (now // ONE_SECOND//2) % 2 == 0:
        screen.blit(game_over, [game_over_x, game_over_y])

    screen.blit(score_text, [center(game, score_text, screen_size), game_over_y + 25])
    screen.blit(stopwatch, [center(game, stopwatch, screen_size), game_over_y + 50])

def reboot(game, screen_size):
    saved_stats = game.ship.get_stats()

    game.projectiles.empty()
    game.enemy_projectiles.empty()
    game.entities.empty()
    game.aliens.empty()
    game.asteroids.empty()
    game.bosses.empty()
    game.explosions.empty()
    game.upgrades.empty()
    game.floating_numbers.empty()
    game.celestials.empty()
    game.fleets.clear()
    game.particles.clear()

    framew = game.selected_sheet.sheet.get_width() // game.ship_frames
    frameh = game.selected_sheet.sheet.get_height()
    game.ship = Ship(game.selected_sheet, 0, 0, game.frame, framew, frameh,
                     columns=game.ship_frames)

    for attr, value in saved_stats.items():
        setattr(game.ship, attr, value)

    game.spawnpoint(game.ship, screen_size, game.selected_sheet, game.ship_frames)

    game.ship_alive = True
    game.ship.hitpoints = game.ship.max_hitpoints
    game.ship.shield = game.ship.max_shield

    for ammo in game.ship.guns_ammo:
        game.ship.guns_ammo[ammo] = game.ship.base_guns_ammo[ammo]

    game.ship.damage = game.ship.base_damage
    game.ship.critical = False

    game.frame = 0
    game.last_update = pygame.time.get_ticks()
    game.last_asteroid_spawn = 0
    game.last_alien_spawn = 0
    game.last_upgrade_spawn = 0
    game.last_celestial_spawn = 0
    game.last_shot_time = 0

    game.state.score = 0
    game.state.phase_index = 0
    game.state.current_phase = game.state.phases[0]
    game.state.phase_start_time = pygame.time.get_ticks()
    game.state.phase_state = PHASE_ACTIVE
    game.state.phase_spawned = False
    game.state.skills_generated = False
    game.state.game_over = False
    game.state.game_over_fx = True
    game.state.survival_bonus = 0

    game.active_upgrade = None
    game.upgrade_start_time = 0

    if hasattr(game.hud, "skill_tab"):
        game.hud.skill_tab.active = False

    game.screen_shake = 0

    if game.state.play_sound:
        game.play_music('odyssey')