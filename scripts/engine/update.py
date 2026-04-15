import random

import pygame

from scripts.engine import upgd
from scripts.engine.collision import check_collision
from scripts.engine.controller import update_controller
from scripts.engine.difficulty import Difficulty
from scripts.engine.input import update_cursor
from scripts.engine.movement import update_movement
from scripts.engine.runtime import get_boss_pos, get_upgrade_position, \
    get_ship_ember
from scripts.engine.shared import joysticks, controller
from scripts.engine.upgd import Upgrade
from scripts.engine.utils import resource_path, formulize
from scripts.objects.asteroid import Asteroid
from scripts.objects.boss import Boss
from scripts.objects.celestial import random_celestial, is_valid_spawn
from scripts.objects.enemies import Alien, HeavyAlien, BomberAlien, EvokerAlien, StoneAlien
from scripts.objects.explode import Explosion
from scripts.objects.particle import Particle
from scripts.system.constants import *

__all__ = ['Updater']


class Updater:
    def update(self, game):
        if not game.state.pause or game.hud.skill_tab.active:
            update_controller(game, game.screen_size, game.delta)
            if not game.hud.skill_tab.active:
                update_movement(game, game.delta, game.screen_size)
                update_cursor(game, game.delta, game.screen_size)

        if not game.state.pause and not game.state.game_over:
            update_game(game, game.delta, game.screen_size, game.hud_padding)
            game.clock.update_time(game)

        if TOGGLE_TUTORIAL:
            game.tutorial.update(game, game.delta)


def set_hud(screen_size):
    width, height = screen_size
    return {'left': 0, 'top': 0, 'right': width, 'bottom': height,
            'width': width, 'height': height}


def spawner(game):
    now = pygame.time.get_ticks()

    if game.state.phase_state != PHASE_ACTIVE:
        return

    if now - game.spawns.last_reinforcement_spawn < SPAWN_COOLDOWN:
        return

    if enemies_alive(game):
        return

    is_boss_phase = (game.state.phase_index == len(game.state.phases) - 1)

    if is_boss_phase:
        if not game.spawns.boss_spawned:
            spawn_boss(game)
            game.spawns.boss_spawned = True
        return

    if game.state.phase_fade <= 0:
        if game.state.phase_index in ALIEN_PHASES:
            spawn_fleet(game)
        elif game.state.phase_index in ASTEROID_PHASES:
            spawn_asteroids(game)
        game.spawns.last_reinforcement_spawn = now


def enemies_alive(game):
    return (any(a.alive() for a in game.sprites.aliens) or
            any(b.alive() for b in game.sprites.bosses))


def update_phase(game):
    now = pygame.time.get_ticks()

    score_goal = SCORE_BASE * game.state.score_scaling

    if game.state.phase_state == PHASE_ACTIVE:
        spawner(game)

        score_goal = game.state.score >= score_goal
        time = now - game.state.phase_start_time >= game.state.phase_length

        if (score_goal or time) and not enemies_alive(game):
            game.state.phase_state = PHASE_CLEANUP

    elif game.state.phase_state == PHASE_CLEANUP:
        if not enemies_alive(game):
            game.state.phase_state = PHASE_TRANSITION
            game.state.transition_started = False

    elif game.state.phase_state == PHASE_TRANSITION:
        if not game.state.transition_started:
            game.state.transition_started = True
            run_transition(game)


def run_transition(game):
    if game.state.phase_state != PHASE_TRANSITION:
        return

    game.state.pause = True
    game.hud.skill_tab.open((pygame.display.Info().current_w // 2 -
                             game.hud.skill_tab.width // 2, 200))

    game.ship.perk_points += 1
    game.state.score_scaling *= SCORE_SCALING_INCREASE

    available_skills = game.skills.skills
    game.state.current_phase_options = random.sample(available_skills,
                                                     k=min(3,
                                                           len(available_skills)))

    game.input.selected_skill_index = 0
    game.input.selected_skill = game.state.current_phase_options[0]
    game.state.skills_generated = True

    game.state.phase_index = (game.state.phase_index + 1) % len(
        game.state.phases)
    game.state.real_phase_index += 1

    game.state.score = 0
    game.state.phase_fade = PHASE_FADE
    game.state.phase_start = True

    game.spawns.last_reinforcement_spawn = pygame.time.get_ticks() + 1000
    game.state.phase_start_time = pygame.time.get_ticks()
    game.state.phase_state = PHASE_ACTIVE
    game.spawns.boss_spawned = False
    game.ship.spawnpoint(game.screen_size, game.sprites.framew)


def spawn_fleet(game):
    formations = ['block', 'clutch', 'cross', 'line']
    formation_type = random.choice(formations)

    x = random.randint(100, game.screen_size[0] - 100)
    y = -300
    center = pygame.Vector2(x, y)
    
    offsets = []
    if formation_type == "block":
        for r in range(3):
            for c in range(3):
                offsets.append((c * 60 - 60, r * 60 - 60))
    elif formation_type == "clutch":
        for _ in range(8):
            offsets.append(
                (random.randint(-100, 100), random.randint(-100, 100)))
    elif formation_type == "cross":
        for i in range(-2, 3):
            offsets.append((i * 60, 0))
            if i != 0:
                offsets.append((0, i * 60))
    elif formation_type == "line":
        length = random.randint(3, 7)
        horizontal = random.choice([True, False])
        for i in range(length):
            if horizontal:
                offsets.append((i * 60 - (length * 30), 0))
            else:
                offsets.append((0, i * 60 - (length * 30)))

    for offset in offsets:
        if game.state.sandbox_enabled:
            match game.state.sandbox_enemy_type:
                case "Alien":
                    alien_type = Alien
                case "Heavy":
                    alien_type = HeavyAlien
                case "Kamikaze":
                    alien_type = BomberAlien
                case _:
                    alien_type = Alien
        else:
            alien_type = random.choices(
                [Alien, HeavyAlien, BomberAlien, EvokerAlien, StoneAlien],
                weights=[0.5, 0.2, 0.15, 0.08, 0.07],
                k=1
            )[0]

        spawn_x = center.x + offset[0]
        spawn_y = center.y + offset[1]

        if alien_type == Alien:
            alien = Alien('red', spawn_x, spawn_y, game.ship, game)
        else:
            alien = alien_type(spawn_x, spawn_y, game.ship, game)

        alien.formation_offset = pygame.Vector2(offset)
        alien.formation_center = center
        game.sprites.aliens.add(alien)


def spawn_asteroids(game):
    if (not game.spawns.can_spawn_asteroids and game.state.difficulty ==
            Difficulty.TOURIST):
        return

    spawns = random.randint(5, 10)
    for _ in range(spawns):
        x = random.randint(0, game.screen_size[0] - 50)
        y = random.randint(*ASTEROID_POS)

        asteroid = Asteroid(game.screen_size[0], min_y=y, max_y=y)

        too_close = any(abs(asteroid.rect.y - a.rect.y) < ASTEROID_MIN_DISTANCE
                        for a in game.sprites.asteroids)
        if too_close:
            asteroid.rect.y -= ASTEROID_OFFSET

        game.sprites.asteroids.add(asteroid)


def spawn_boss(game):
    if not game.state.phase_spawned and not game.state.pause:
        x, y = get_boss_pos()
        color = ['red', 'green', 'yellow']

        match game.state.difficulty:
            case Difficulty.TOURIST:
                game.spawns.boss_count = 0
            case Difficulty.EXPLORER:
                game.spawns.boss_count = 1
            case Difficulty.PILOT:
                game.spawns.boss_count = 2
            case Difficulty.NIGHTMARE:
                game.spawns.boss_count = 3

        if game.spawns.boss_count > 0:
            for i in range(game.spawns.boss_count):
                game.sprites.bosses.add(
                    Boss(game, game.ship, game.sprites.enemy_projectiles, x, y,
                         random.choice(color)))

        game.play_music('flight')
        game.spawns.phase_spawned = True
        game.spawns.boss_alive = True


def update_shockwaves(game):
    for wave in list(game.sprites.shockwaves):
        wave.update()

        for asteroid in list(game.sprites.asteroids):
            if wave.affects(asteroid.rect.center):
                game.sprites.explosions.add(Explosion(asteroid.rect.centerx,
                                                      asteroid.rect.centery,
                                                      game.sprites.frame_big_explode))
                game.state.score += game.ship.level * SCORE_SCALING * game.state.score_multiplier
                game.ship.gain_xp(formulize(game, game.ship.level),
                                  game.mixer.sounds)
                asteroid.kill()

        for alien in list(game.sprites.aliens):
            if wave.affects(alien.rect.center):
                if hasattr(alien, "explode"):
                    alien.explode()
                else:
                    game.sprites.explosions.add(Explosion(alien.rect.centerx,
                                                          alien.rect.centery,
                                                          game.sprites.frame_big_explode))
                    game.state.score += (
                                game.ship.level * SCORE_SCALING * game.state.score_multiplier)
                    game.ship.gain_xp(formulize(game, game.ship.level),
                                      game.mixer.sounds)
                    alien.kill()

        for a in list(game.sprites.asteroids):
            if not a.alive():
                a.kill()

        for a in list(game.sprites.aliens):
            if not a.alive():
                a.kill()

        if not wave.alive:
            game.sprites.shockwaves.remove(wave)


def cleanup_groups(game):
    for group in [game.sprites.aliens,
                  game.sprites.asteroids,
                  game.sprites.projectiles]:
        for sprite in list(group):
            if not sprite.alive():
                group.remove(sprite)


def update_game(game, delta, screen_size, hud_padding):
    game.ship.hit = False

    if game.ship.hit:
        game.ship.combo_multiplier = 1.0

    cleanup_groups(game)
    for i in game.sprites.stars:
        if not game.state.pause:
            if game.state.phase_start and game.state.phase_fade > 0:
                i[1] += LIGHT_SPEED
                game.state.phase_fade -= 1
                if game.state.phase_fade <= 0:
                    game.state.phase_start = False
            else:
                i[1] += game.state.stars_speed

        if i[1] > screen_size[1]:
            i[1] = 0
            i[0] = random.randint(0, screen_size[0])

    current_time = pygame.time.get_ticks()
    if current_time - game.spawns.last_celestial_spawn > game.spawns.celestial_spawn_interval:
        game.spawns.last_celestial_spawn = current_time
        for _ in range(random.randint(1, 4)):
            for _ in range(10):
                new_celestial = random_celestial(game)
                if new_celestial and is_valid_spawn(new_celestial,
                                                    game.sprites.celestials,
                                                    CELESTIAL_MIN_DISTANCE):
                    game.sprites.celestials.add(new_celestial)
                    break

    if current_time - game.spawns.last_upgrade_spawn > game.spawns.upgrade_spawn_interval:
        game.spawns.last_upgrade_spawn = current_time

        for _ in range(random.randint(1, 2)):
            x, y = get_upgrade_position()
            game.spawns.last_upgrade = upgd.get_upgrade()
            upgrade_type = game.spawns.last_upgrade
            upgrade_path = resource_path(f"assets/{upgrade_type}.png")
            new_upgrade = Upgrade(upgrade_path, x, y, upgrade_type=upgrade_type)
            game.sprites.upgrades.add(new_upgrade)  # type: ignore

    now = pygame.time.get_ticks()
    if now - game.sprites.last_update_base > game.sprites.cooldown_base:
        game.sprites.anim_frame_base += 1
        game.sprites.last_update_base = now

    if now - game.sprites.last_update_overlay > game.sprites.cooldown_overlay:
        game.sprites.anim_frame_overlay += 1
        game.sprites.last_update_overlay = now

    if game.ship.direction in ["left", "right"]:
        if game.ship.direction == "left":
            frames = game.sprites.left_frames_movement
            if game.sprites.last_direction != "left":
                game.sprites.anim_index_left = len(frames) - 1
                game.sprites.last_update_left = now
                game.sprites.last_direction = "left"

            if now - game.sprites.last_update_left > game.sprites.cooldown_base:
                game.sprites.anim_index_left -= 1
                if game.sprites.anim_index_left < 0:
                    game.sprites.anim_index_left = 0
                game.sprites.last_update_left = now
            game.sprites.base = frames[game.sprites.anim_index_left]

        else:
            frames = game.sprites.right_frames_movement
            if game.sprites.last_direction != "right":
                game.sprites.anim_index_right = 0
                game.sprites.last_update_right = now
                game.sprites.last_direction = "right"

            if now - game.sprites.last_update_right > game.sprites.cooldown_base:
                game.sprites.anim_index_right += 1
                if game.sprites.anim_index_right >= len(frames):
                    game.sprites.anim_index_right = len(frames) - 1
                game.sprites.last_update_right = now
            game.sprites.base = frames[game.sprites.anim_index_right]
    else:
        game.sprites.base = game.sprites.frame_idle
        game.sprites.last_direction = None

    game.sprites.celestials.update()
    game.sprites.asteroids.update()
    game.sprites.aliens.update()
    game.sprites.enemy_projectiles.update()

    if game.sprites.ship_alive:
        game.ship.update_upgrades()
        game.ship._overheat_cooldown(game, delta)
        if game.ship.hitpoints < (game.ship.max_hitpoints * 0.25):
            game.ship.critical = True
            frequency = 0
            if game.ship.critical and game.state.can_screen_shake:
                game.screen_shake = SCREEN_SHAKE * 2
                if joysticks and game.state.can_rumble:
                    controller.rumble(frequency, 3, BASE_RUMBLE_MS * 2)
                game.mixer.play(6)
                frequency += 0.1

        game.ship.update_position(game.ship.rect.x, game.ship.rect.y)
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
            game.sprites.particles.append(particle)

    game.sprites.bosses.update()
    game.sprites.projectiles.update()
    game.sprites.enemy_projectiles.update()

    game.sprites.floating_numbers.update(delta)
    game.sprites.explosions.update()
    game.sprites.upgrades.update()

    for particle in game.sprites.particles[:]:
        particle.update()
        if particle.timer <= 0:
            game.sprites.particles.remove(particle)

    if not game.sprites.direction_set:
        game.ship.direction = "idle"

    check_collision(game, game.local)
    update_shockwaves(game)

    game.state.survival_bonus += 1
    if game.state.survival_bonus >= FPS:
        game.state.survival_bonus = 0
        game.state.score += 1 * game.state.score_multiplier

    now = pygame.time.get_ticks()
    if now - game.spawns.last_hole_spawn >= game.spawns.black_hole_spawn_delay:
        game.spawns.last_hole_spawn = now
        if random.random() < 0.1:
            game.events.black_hole_event(game)

    update_phase(game)
