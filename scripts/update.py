import random

import pygame

from scripts import upgd
from scripts.asteroid import Asteroid
from scripts.boss import Boss
from scripts.celestial import random_celestial, is_valid_spawn
from scripts.collision import check_collision
from scripts.explode import Explosion
from scripts.fleet import spawn_fleet
from scripts.particle import Particle
from scripts.runtime import get_boss_pos, get_upgrade_position, get_ship_ember
from scripts.settings import *
from scripts.shared import joysticks, controller
from scripts.upgd import Upgrade
from scripts.utils import resource_path


def set_hud(screen_size):
    width, height = screen_size
    return {'left': 0, 'top': 0, 'right': width, 'bottom': height,
            'width': width, 'height': height}

def update_phase(game):
    current_time = pygame.time.get_ticks()
    elapsed = current_time - game.state.phase_start_time
    buffer_time = PHASE_BUFFER_TIME

    if elapsed >= game.state.phase_length - buffer_time:
        game.state.phase_ending = True

    if not game.state.phase_spawned:
        if game.state.phase_index < len(game.state.phases) - 1:
            spawn_fleet(game, game.state.phase_index)

        if game.state.phase_index in ASTEROID_PHASES:
            spawn_asteroids(game)

        if game.state.current_phase == game.state.phases[-1]:
            spawn_boss(game)

        game.state.phase_spawned = True

    enemies_alive = (
            any(alien.alive() for alien in game.aliens) or
            any(boss.alive() for boss in game.bosses)
    )

    if (not game.hud.skill_tab.active and game.state.phase_ending and not enemies_alive
            and not game.state.skills_generated):
        game.hud.skill_tab.open((pygame.display.Info().current_w // 2 -
                             game.hud.skill_tab.width // 2, 200))
        game.ship.perk_points += 1

        available_skills = game.skills.skills
        current_choices = [s for s in available_skills if
                               s not in game.state.current_phase_options]
        game.state.current_phase_options = random.sample(
            current_choices, k=min(3, len(current_choices))
        )
        game.input.selected_skill_index = 0
        game.input.selected_skill = game.state.current_phase_options[0]
        game.state.skills_generated = True

    if game.hud.skill_tab.active:
        game.state.pause = True
    else:
        game.state.pause = False

    if (game.state.phase_ending and not enemies_alive and not
            game.hud.skill_tab.active):
        game.state.phase_index += 1
        if game.state.phase_index >= len(game.state.phases):
            game.state.phase_index = 0
        game.state.current_phase = game.state.phases[game.state.phase_index]
        game.state.phase_start_time = current_time
        game.state.phase_ending = False
        game.last_alien_spawn = 0
        game.last_asteroid_spawn = 0
        game.state.phase_spawned = False
        game.state.current_phase_options = []
        game.state.skills_generated = False

def spawn_asteroids(game):
    if game.state.phase_ending:
        return

    if game.state.phase_index not in ASTEROID_PHASES:
        return

    spawns = random.randint(5, 10)
    for _ in range(spawns):
        x = random.randint(0, game.screen_size[0] - 50)
        y = random.randint(*ASTEROID_POS)

        asteroid = Asteroid(game.screen_size[0], min_y=y, max_y=y)

        too_close = any(abs(asteroid.rect.y - a.rect.y) < ASTEROID_MIN_DISTANCE
                        for a in game.asteroids)
        if too_close:
            asteroid.rect.y -= ASTEROID_OFFSET

        game.asteroids.add(asteroid)
        game.entities.add(asteroid)

    game.last_asteroid_spawn = pygame.time.get_ticks()

def spawn_boss(game):
    if not game.state.phase_spawned and not game.state.pause:
        x, y = get_boss_pos()
        color = ['red', 'green', 'yellow']
        boss = Boss(game, game.ship, game.enemy_projectiles, x, y,
                    random.choice(color))
        game.play_music('flight')
        game.bosses.add(boss)
        game.state.phase_spawned = True
        game.boss_alive = True

def update_shockwaves(game):
    for wave in list(game.shockwaves):
        wave.update()

        for asteroid in list(game.asteroids):
            if wave.affects(asteroid.rect.center):
                game.explosions.add(Explosion(asteroid.rect.centerx,
                              asteroid.rect.centery,
                              game.frame_big_explode))
                asteroid.kill()

        for alien in list(game.aliens):
            if wave.affects(alien.rect.center):
                game.explosions.add(Explosion(alien.rect.centerx,
                              alien.rect.centery,
                              game.frame_big_explode))
                alien.kill()

        if not wave.alive:
            game.shockwaves.remove(wave)

def update_game(game, delta, screen_size, hud_padding):
    game.ship.hit = False

    if game.ship.hit:
        game.ship.combo_multiplier = 1.0

    for i in game.stars:
        if not game.state.pause:
            i[1] += game.state.stars_speed
        if i[1] > screen_size[1]:
            i[1] = 0
            i[0] = random.randint(0, screen_size[0])

    current_time = pygame.time.get_ticks()
    if current_time - game.last_celestial_spawn > game.celestial_spawn_interval:
        game.last_celestial_spawn = current_time
        for _ in range(random.randint(1, 4)):
            for _ in range(10):
                new_celestial = random_celestial()
                if new_celestial and is_valid_spawn(new_celestial, game.celestials,
                                                    CELESTIAL_MIN_DISTANCE):
                    game.celestials.add(new_celestial)
                    break

    if current_time - game.last_upgrade_spawn > game.upgrade_spawn_interval:
        game.last_upgrade_spawn = current_time

        for _ in range(random.randint(1, 2)):
            x, y = get_upgrade_position()
            game.last_upgrade = upgd.get_upgrade()
            upgrade_type = game.last_upgrade
            upgrade_path = resource_path(f"assets/{upgrade_type}.png")
            new_upgrade = Upgrade(upgrade_path, x, y, upgrade_type=upgrade_type)
            game.upgrades.add(new_upgrade)  # type: ignore

    now = pygame.time.get_ticks()
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

    if game.ship_alive:
        game.ship.update_position(game.ship_x, game.ship_y)
        if game.ship_alive:
            game.ship.update_upgrades()
            if game.ship.hitpoints < (game.ship.max_hitpoints * 0.25):
                game.ship.critical = True
                frequency = 0
                if game.ship.critical:
                    game.screen_shake = SCREEN_SHAKE * 2
                    if joysticks:
                        controller.rumble(0.5, frequency, BASE_RUMBLE_MS * 2)
                    game.sounds[5].play()
                    frequency += 0.1

            game.ship.update_position(game.ship_x, game.ship_y)
            trail_pos = game.ship.hitbox.midbottom
            hp_ratio = game.ship.hitpoints / game.ship.max_hitpoints
            num_particles = int(8 * (1 - hp_ratio))
            if hp_ratio < 0.2:
                color = get_ship_ember()
            color = COLOR_WHITE if hp_ratio > 0.5 else COLOR_SMOKE
            for _ in range(num_particles):
                velocity = pygame.Vector2(random.uniform(-1, 1),
                                          random.uniform(2, 4))
                particle = Particle(trail_pos, velocity, timer=80,
                                    color=color, radius=4)
                game.particles.append(particle)

    game.fleets = [f for f in game.fleets if any(a.alive() for a in f.aliens)]
    for fleet in game.fleets:
        fleet.update()

    if game.state.current_phase == game.state.phases[-1]:
        game.bosses.update()

    game.projectiles.update()
    game.enemy_projectiles.update()

    game.floating_numbers.update(delta)
    game.explosions.update()
    game.upgrades.update()

    for particle in game.particles[:]:
        particle.update()
        if particle.timer <= 0:
            game.particles.remove(particle)

    if not game.direction_set:
        game.ship.direction = "idle"

    check_collision(game)
    update_shockwaves(game)

    game.state.survival_bonus += 1
    if game.state.survival_bonus >= FPS:
        game.state.survival_bonus = 0
        game.state.score += 1 * game.state.score_multiplier

    now = pygame.time.get_ticks()
    if now - game.state.last_hole_spawn >= game.state.black_hole_spawn_delay:
        game.state.last_hole_spawn = now
        if random.random() < 0.1:
            game.events.black_hole_event(game)

    update_phase(game)