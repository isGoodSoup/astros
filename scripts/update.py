import random

import pygame as pg

from scripts import upgd
from scripts.asteroid import Asteroid
from scripts.boss import Boss
from scripts.celestial import random_celestial, is_valid_spawn
from scripts.collision import check_collision
from scripts.fleet import spawn_fleet
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
    buffer_time = 5000

    if elapsed >= game.phase_length - buffer_time:
        game.phase_ending = True

    if not game.phase_spawned:
        print(f"Spawning phase {game.current_phase}")
        if game.current_phase == game.phases[-1]:
            spawn_boss(game)
        elif game.current_phase in [game.phases[3], game.phases[5]]:
            spawn_asteroids(game)
        else:
            spawn_fleet(game, game.current_phase)
            print(f"Aliens spawned: {len(game.aliens)}")
        game.phase_spawned = True

    fleets_alive = any(len(fleet.aliens) > 0 for fleet in game.fleets)
    enemies_alive = any([
        len(game.aliens) > 0,
        len(game.asteroids) > 0,
        len(game.bosses) > 0,
        fleets_alive])

    if game.phase_ending and not game.skill_tab.active\
            and not enemies_alive:
        game.ship.perk_points += 1
        game.skill_tab.active = True

    if game.skill_tab.active:
        if game.skill_tab.pos == game.skill_tab.target_pos:
            game.pause = True
            game.phase_index = (game.phase_index + 1) % len(game.phases)
            game.current_phase = game.phases[game.phase_index]
            game.phase_start_time = pg.time.get_ticks()
            game.phase_ending = False
            game.last_alien_spawn = 0
            game.last_asteroid_spawn = 0
            game.phase_spawned = False

    if game.phase_ending and not game.current_phase_options:
        available_skills = [s for s in game.skills.skills if not s.unlocked]
        if not available_skills:
            available_skills = game.skills.skills
        game.current_phase_options = random.sample(available_skills, k=min(3,len(available_skills)))
        game.selected_skill = game.current_phase_options[0]

def spawn_asteroids(game):
    current_time = pg.time.get_ticks()
    if current_time - game.last_asteroid_spawn > game.asteroid_spawn_interval:
        game.last_asteroid_spawn = current_time
        for _ in range(random.randint(1, game.asteroid_spawn_count)):
            attempts = 0
            while attempts < 20:
                new_asteroid = Asteroid(game.screen_size[0], min_y=-200, max_y=-50)
                if all(abs(new_asteroid.rect.y - a.rect.y) >= 60 for a in
                       game.asteroids):
                    game.asteroids.add(new_asteroid)
                    game.entities.add(new_asteroid)
                    break
                attempts += 1

def spawn_boss(game):
    if not game.boss_spawned:
        x = game.screen_size[0] // 2
        y = 350
        color = ['red', 'green', 'yellow']
        boss = Boss(game.ship, x, y, random.choice(color))
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
    game.asteroids.update()

    alive_fleets = []
    for fleet in game.fleets:
        fleet.update()
        if fleet.aliens:
            alive_fleets.append(fleet)
    game.fleets = alive_fleets

    if game.current_phase == game.phases[-1]:
        game.bosses.update()

    if not game.pause:
        game.projectiles.update()
        game.enemy_projectiles.update()

    game.explosions.update()
    game.upgrades.update()
    game.skill_tab.update()
    game.stats_tab.update()
    game.floating_numbers.update(delta)

    if game.skill_tab.pos == game.skill_tab.start_pos:
        game.current_phase_options = []

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

    update_phase(game)

def update_hud(game, font, screen, hud_ratio):
    game.stopwatch = font.render(f"{game.hours:02}:{game.minutes:02}:{game.seconds:02}", True, "WHITE")
    screen.blit(game.stopwatch,
                [hud_ratio['left'] + hud_ratio['width'] // 2 -
                 game.stopwatch.get_width() // 2, hud_ratio['top']])

    score_text = f"{int(game.score):06}"
    high_score = f"{int(game.high_score):06}"
    score_surface = font.render(score_text, True, "WHITE")
    high_score_surface = font.render(high_score, True, "WHITE")

    line_spacing = 2

    score_lines = ["", "SCORE"]
    score_line_surfs = [font.render(line, True, "WHITE") for line in score_lines]

    title_height = sum(s.get_height() for s in score_line_surfs) + line_spacing * (len(score_line_surfs) - 1)
    score_value_y = hud_ratio['top'] + title_height + 5

    screen.blit(score_surface, [hud_ratio['left'], score_value_y])

    y = score_value_y - 5
    for surf in reversed(score_line_surfs):
        y -= surf.get_height()
        screen.blit(surf, [hud_ratio['left'], y])
        y -= line_spacing

    high_lines = ["HIGH", "SCORE"]
    high_line_surfs = [font.render(line, True, "WHITE") for line in high_lines]

    block_width = max(s.get_width() for s in high_line_surfs + [high_score_surface])
    x_pos = hud_ratio['right'] - block_width
    screen.blit(high_score_surface, [x_pos, score_value_y])

    y = score_value_y - 5
    for surf in reversed(high_line_surfs):
        y -= surf.get_height()
        screen.blit(surf, [x_pos, y])
        y -= line_spacing

    total_frames = len(game.hitpoints.frames) - 1
    if game.ship.hitpoints <= 0:
        hitpoints_frame = total_frames
    else:
        hitpoints_frame = (total_frames - (game.ship.hitpoints * total_frames)
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
    ammo_frame = (ammo_total_frames - (game.ship.ammo * ammo_total_frames)
                  // game.ship.base_ammo)
    ammo_frame = max(0, min(ammo_total_frames, ammo_frame))
    game.ammo.update(game.ship, hud_ratio, ['right', 'bottom'], ammo_frame,
                     screen)
