import random

import pygame

from scripts import upgd
from scripts.asteroid import Asteroid
from scripts.boss import Boss
from scripts.celestial import random_celestial, is_valid_spawn
from scripts.collision import check_collision
from scripts.fleet import spawn_fleet
from scripts.particle import Particle
from scripts.toggles import tutorial_on
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
    current_time = pygame.time.get_ticks()
    elapsed = current_time - game.state.phase_start_time
    buffer_time = 5000

    if elapsed >= game.state.phase_length - buffer_time:
        game.state.phase_ending = True

    if not game.state.phase_spawned:
        if game.state.current_phase == game.state.phases[-1]:
            spawn_boss(game)
        elif game.state.current_phase in [game.state.phases[3], game.state.phases[5]]:
            spawn_asteroids(game)
        else:
            spawn_fleet(game, game.state.current_phase)
        game.state.phase_spawned = True

    fleets_alive = any(len(fleet.aliens) > 0 for fleet in game.fleets)
    enemies_alive = any([
        len(game.aliens) > 0,
        len(game.asteroids) > 0,
        len(game.bosses) > 0,
        fleets_alive
    ])

    if (game.state.phase_ending and not game.hud.skill_tab.active and not enemies_alive
            and not game.state.skills_generated):
        game.hud.skill_tab.open((pygame.display.Info().current_w // 2 -
                             game.hud.skill_tab.width // 2, 200))
        available_skills = [s for s in game.skills.skills if not s.unlocked]
        if not available_skills:
            available_skills = game.skills.skills
        game.state.current_phase_options = random.sample(
            available_skills, k=min(3, len(available_skills)))
        game.state.skills_generated = True

    if game.hud.skill_tab.active:
        game.state.pause = True
        if game.state.pause:
            game.ship.perk_points += 1

    if not game.hud.skill_tab.active and game.state.phase_ending and not enemies_alive:
        game.state.pause = False
        game.state.phase_index = (game.state.phase_index + 1) % len(game.state.phases)
        game.state.current_phase = game.state.phases[game.phase_index]
        game.state.phase_start_time = current_time
        game.state.phase_ending = False
        game.last_alien_spawn = 0
        game.last_asteroid_spawn = 0
        game.state.phase_spawned = False
        game.state.current_phase_options = []
        game.state.skills_generated = False

def spawn_asteroids(game):
    current_time = pygame.time.get_ticks()
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
    if not game.state.phase_spawned:
        x = game.screen_size[0] // 2
        y = 350
        color = ['red', 'green', 'yellow']
        boss = Boss(game.ship, x, y, random.choice(color))
        game.bosses.add(boss)
        game.state.phase_spawned = True
        game.boss_alive = True

def update_game(game, delta, screen_size, hud_padding):
    game.ship.hit = False
    for i in game.stars:
        if not game.state.pause:
            i[1] += game.state.stars_speed
        if i[1] > screen_size[1]:
            i[1] = 0
            i[0] = random.randint(0, screen_size[0])

    if not tutorial_on:
        current_time = pygame.time.get_ticks()
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
        if not game.ship.moved_down:
            trail_pos = game.ship.hitbox.midbottom
            for _ in range(8):
                velocity = pygame.Vector2(random.uniform(-1, 1),
                                      random.uniform(2, 4))
                particle = Particle(trail_pos, velocity, timer=80,
                                    color=(255, 255, 255), radius=4)
                game.particles.append(particle)

    alive_fleets = []
    for fleet in game.fleets:
        fleet.update()
        if fleet.aliens:
            alive_fleets.append(fleet)
    game.fleets = alive_fleets

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
    current_time = pygame.time.get_ticks()
    if game.active_upgrade == "power_up":
        game.ship.damage = game.ship.base_damage * game.ship.damage_multiplier * 2
        if current_time - game.upgrade_start_time >= game.upgrade_duration:
            game.active_upgrade = None
            game.ship.damage = game.ship.base_damage

    game.state.survival_bonus += 1
    if game.state.survival_bonus >= 60:
        game.state.survival_bonus = 0
        game.state.score += 1 * game.state.score_multiplier

    update_phase(game)