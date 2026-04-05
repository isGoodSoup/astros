import random

import pygame as pg
import pygame.display

from scripts import upgd
from scripts.asteroid import Asteroid
from scripts.boss import Boss
from scripts.celestial import random_celestial, is_valid_spawn
from scripts.collision import check_collision
from scripts.fleet import spawn_phase_aliens
from scripts.upgd import Upgrade


def set_hud(screen_size, padding):
    width, height = screen_size
    return {
        'left': padding,
        'top': padding,
        'right': width - padding,
        'bottom': height - padding,
        'width': width - 2 * padding,
        'height': height - 2 * padding
    }

def update_phase(game):
    current_time = pg.time.get_ticks()

    if not hasattr(game, "phase_start_time"):
        game.phase_start_time = current_time
        game.phase_ending = False

    elapsed = current_time - game.phase_start_time
    if not hasattr(game, "phase_length"):
        game.phase_length = random.randint(20_000, 30_000)
    buffer_time = 5000

    if elapsed >= game.phase_length - buffer_time:
        game.phase_ending = True

    if game.current_phase == "boss_fight":
        spawn_boss(game)

    if game.phase_ending:
        if not game.aliens and not game.asteroids and not game.bosses:
            game.phase_index = (game.phase_index + 1) % len(game.phases)
            game.current_phase = game.phases[game.phase_index]
            game.phase_start_time = current_time
            game.phase_ending = False
            game.last_alien_spawn = 0
            game.last_asteroid_spawn = 0
            game.boss_spawned = False
    else:
        if game.current_phase == "asteroids" and not game.phase_ending:
            spawn_asteroids(game)
        elif game.current_phase in ("quiet", "aliens", "asteroids"):
            spawn_phase_aliens(game, game.current_phase)

def spawn_asteroids(game):
    current_time = pg.time.get_ticks()
    if current_time - game.last_asteroid_spawn > game.asteroid_spawn_interval:
        game.last_asteroid_spawn = current_time
        for _ in range(random.randint(1, game.asteroid_spawn_count)):
            for _ in range(10):
                new_asteroid = Asteroid(game.screen_size[0], min_y=-200,
                                        max_y=-50)
                too_close = any(
                    abs(new_asteroid.rect.y - a.rect.y) < 60 for a in
                    game.asteroids)
                if not too_close:
                    new_asteroid.hitpoints = int(
                        new_asteroid.hitpoints * game.asteroid_hitpoints)
                    new_asteroid.speed = game.asteroid_speed
                    game.asteroids.add(new_asteroid)
                    break

def spawn_boss(game):
    if not game.boss_spawned:
        x = game.screen_size[0] // 2
        y = 100
        color = 'red'
        boss = Boss(game.ship, x, y, color)
        game.bosses.add(boss)
        game.boss_spawned = True
        game.boss_alive = True

def update_game(game, delta, screen_size, hud_padding):
    game.ship.hit = False
    for i in game.stars:
        if not game.pause:
            i[1] += game.stars_speed
        if i[1] > screen_size[1]:
            i[1] = 0
            i[0] = random.randint(0, screen_size[0])

    if not game.tutorial_on:
        current_time = pg.time.get_ticks()
        if current_time - game.last_celestial_spawn > game.celestial_spawn_interval:
            game.last_celestial_spawn = current_time
            for _ in range(random.randint(1, 4)):
                for _ in range(10):
                    new_celestial = random_celestial()
                    if new_celestial and is_valid_spawn(new_celestial, game.celestials,
                                                        200):
                        game.celestials.add(new_celestial)
                        break

        if current_time - game.last_upgrade_spawn > game.upgrade_spawn_interval:
            game.last_upgrade_spawn = current_time

            for _ in range(random.randint(1, 2)):
                x = random.randint(0, screen_size[0])
                y = random.randint(-200, -50)

                game.last_upgrade = upgd.get_upgrade()
                upgrade = f"assets/{game.last_upgrade}.png"
                new_upgrade = Upgrade(upgrade, x, y)
                game.upgrades.add(new_upgrade)  # type: ignore

        update_phase(game)

    now = pg.time.get_ticks()
    if now - game.last_update_base > game.cooldown_base:
        game.anim_frame_base += 1
        game.last_update_base = now

    if now - game.last_update_overlay > game.cooldown_overlay:
        game.anim_frame_overlay += 1
        game.last_update_overlay = now

    if game.ship.direction in ["left", "right"]:
        if game.ship.direction == "left":
            frames = game.left_frames_movement
            if game.last_direction != "left":
                game.anim_index_left = len(frames) - 1
                game.last_update_left = now
                game.last_direction = "left"

            if now - game.last_update_left > game.cooldown_base:
                game.anim_index_left -= 1
                if game.anim_index_left < 0:
                    game.anim_index_left = 0
                game.last_update_left = now
            game.base = frames[game.anim_index_left]

        else:
            frames = game.right_frames_movement
            if game.last_direction != "right":
                game.anim_index_right = 0
                game.last_update_right = now
                game.last_direction = "right"

            if now - game.last_update_right > game.cooldown_base:
                game.anim_index_right += 1
                if game.anim_index_right >= len(frames):
                    game.anim_index_right = len(frames) - 1
                game.last_update_right = now
            game.base = frames[game.anim_index_right]
    else:
        game.base = game.frame_idle
        game.last_direction = None

    game.celestials.update()
    if game.current_phase == "asteroids":
        game.entities.add(game.asteroids)
        game.entities.update()
    elif game.current_phase != "asteroids":
        for asteroid in game.asteroids:
            asteroid.rect.y -= 2
            if asteroid.rect.y > pygame.display.Info().current_h:
                game.asteroids.remove(asteroid)

    if game.current_phase in ("quiet", "asteroids"):
        game.entities.add(game.aliens)
        game.entities.update()
        # if random.random() > 0.4:
        #     for alien in game.aliens:
        #         new_proj = alien.shoot(game.base, alien.shot_cooldown, game.play_sound, game.sounds)
        #         game.enemy_projectiles.add(new_proj)

    for fleet in game.fleets:
        fleet.update()

    if game.current_phase == "boss_fight":
        game.bosses.update()

    game.projectiles.update()
    game.explosions.update()
    game.upgrades.update()
    game.skill_tab.update()
    game.stats_tab.update()
    game.floating_numbers.update(delta)

    for particle in game.particles[:]:
        particle.update()
        if particle.timer <= 0:
            game.particles.remove(particle)

    if not game.direction_set:
        game.ship.direction = "idle"

    if game.ship_alive:
        game.ship.update_position(game.ship_x, game.ship_y)

    check_collision(game)
    current_time = pg.time.get_ticks()
    if game.active_upgrade == "power_up":
        game.ship.damage = game.ship.base_damage * game.ship.damage_multiplier * 2
        if current_time - game.upgrade_start_time >= game.upgrade_duration:
            game.active_upgrade = None
            game.ship.damage = game.ship.base_damage

    game.survival_bonus += 1
    if game.survival_bonus >= 60:
        game.survival_bonus = 0
        game.score += 1 * game.score_multiplier

def update_hud(game, font, screen, hud_ratio):
    game.stopwatch = font.render(
        f"{game.hours:02}:{game.minutes:02}:{game.seconds:02}",
        True, "WHITE")
    screen.blit(game.stopwatch,
                [hud_ratio['left'] + hud_ratio['width'] // 2 -
                 game.stopwatch.get_width() // 2, hud_ratio['top']])

    score_text = f"{int(game.score):06}"
    high_score = f"{int(game.high_score):06}"
    score_title = "SCORE"
    high_score_title = "HIGH\nSCORE"

    score_surface = font.render(score_text, True, "WHITE")
    score_title_surface = font.render(score_title, True, "WHITE")
    high_score_surfaces = [font.render(line, True, "WHITE")
                           for line in high_score_title.split('\n')]
    high_score_surface = font.render(high_score, True, "WHITE")

    score_x = hud_ratio['left']
    score_y = hud_ratio['top']
    screen.blit(score_title_surface,
                [score_x, score_y - score_title_surface.get_height() - 5])
    screen.blit(score_surface, [score_x, score_y])

    y_pos = hud_ratio['top']
    x_pos = hud_ratio['right'] - max(s.get_width() for s in
        high_score_surfaces + [high_score_surface])

    for line_surf in high_score_surfaces:
        screen.blit(line_surf, [x_pos, y_pos])
        y_pos += line_surf.get_height() + 2
    screen.blit(high_score_surface, [x_pos, y_pos])

    total_frames = len(game.hitpoints.frames) - 1
    if game.ship.hitpoints <= 0:
        hitpoints_frame = total_frames
    else:
        hitpoints_frame = (
                    total_frames - (game.ship.hitpoints * total_frames)
                    // game.ship.max_hitpoints)
        hitpoints_frame = max(0, min(hitpoints_frame, total_frames))
    game.hitpoints.update(game.ship, hud_ratio, ['right', 'bottom'],
                          hitpoints_frame, screen)

    shield_total_frames = len(game.shield.frames) - 1
    shield_frame = (shield_total_frames - (
                game.ship.shield * shield_total_frames)
                    // game.ship.max_shield)
    shield_frame = max(0, min(shield_total_frames, shield_frame))
    game.shield.update(game.ship, hud_ratio, ['right', 'bottom'],
                       shield_frame, screen)

    experience_total_frames = len(game.xp.frames) - 1
    xp_frame = (experience_total_frames - (
                experience_total_frames * game.ship.xp)
                // game.ship.xp_to_next_level)
    game.xp.update(game.ship, hud_ratio, ['right', 'bottom'], xp_frame,
                   screen)

    ammo_total_frames = len(game.ammo.frames) - 1
    ammo_frame = (shield_total_frames - (game.ship.ammo * ammo_total_frames)
                  // game.ship.base_ammo)
    ammo_frame = max(0, min(ammo_total_frames, ammo_frame))
    game.ammo.update(game.ship, hud_ratio, ['right', 'bottom'], ammo_frame,
                     screen)
