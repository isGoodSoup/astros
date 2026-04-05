import random

import pygame as pg

from scripts.explode import Explosion
from scripts.floaty import FloatingNumber
from scripts.impact import ImpactFrame
from scripts.particle import Particle
from scripts.utils import add_multiplier, formulize


def check_collision(game):
    if game.current_phase == "asteroids":
        asteroid_hit = pg.sprite.spritecollideany(game.ship, game.asteroids, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.hitbox))
    else:
        asteroid_hit = None

    if game.current_phase in ("quiet", "asteroids"):
        alien_hit = pg.sprite.spritecollideany(game.ship, game.aliens, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.hitbox))
    else:
        alien_hit = None

    if game.current_phase in ("quiet", "asteroids"):
        alien_proj = pg.sprite.spritecollideany(game.ship, game.enemy_projectiles, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.rect))
    else:
        alien_proj = None

    if asteroid_hit or alien_hit or alien_proj:
        if random.random() <= game.ship.evasion:
            x, y = asteroid_hit.rect.center
            game.floating_numbers.add(FloatingNumber(
                x, y, "MISS", color=(255, 255, 100)))  # type: ignore
            return

        game.ship.hit = True
        if game.ship.damage_multiplier > 1.0:
            x, y = game.ship.rect.centerx, game.ship.rect.top
            game.floating_numbers.add(FloatingNumber(
                x, y, "NO MULT!", color=(255, 0, 0)))  # type: ignore
            game.ship.damage_multiplier = 1.0

        ship_center_x = game.ship.rect.centerx
        ship_center_y = game.ship.rect.centery
        explosion = Explosion(ship_center_x, ship_center_y,
                              game.frame_explode)
        game.explosions.add(explosion)  # type: ignore

        for _ in range(10):
            vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
            game.particles.append(
                Particle((ship_center_x, ship_center_y), vel))

        if game.play_sound:
            game.sounds[1].play()

        if asteroid_hit:
            asteroid_hit.kill()

        if alien_hit:
            alien_hit.kill()

        damage_per_frame = 0
        if game.ship.shield > 0:
            damage_per_frame = (max(1,
                                    game.ship.max_shield // 33) * game.ship.level)
            game.ship.shield -= damage_per_frame
        else:
            damage_per_frame = max(1,
                                   game.ship.max_hitpoints // 28) * game.ship.level
            game.ship.hitpoints -= damage_per_frame

        if hasattr(game.ship, "fortified_percent"):
            if game.ship.fortified_percent > 0:
                shield_gain = int(
                    damage_per_frame * game.ship.fortified_percent)
                if hasattr(game.ship, "fortified_cap"):
                    shield_gain = min(shield_gain, game.ship.fortified_cap)
                game.ship.shield += shield_gain

        game.screen_shake = 20

        if game.ship.hitpoints <= 0:
            game.game_over = True
            game.ship.kill()
            game.ship_alive = False
            pg.mixer.music.stop()
            game.game_over = True

    hits1 = pg.sprite.groupcollide(game.projectiles, game.asteroids, True,
                                   False)
    for asteroid in hits1.values():
        current_time = pg.time.get_ticks()
        if current_time > game.ship.maniac_boost_end:
            game.ship.maniac_boost = 0

        effective_crit_chance = min(1.0, (
                game.ship.crit_chance / 100) + game.ship.maniac_boost)
        if random.random() < effective_crit_chance:
            damage_per_frame = game.ship.damage * game.ship.crit_multiplier
            color = (255, 50, 50)
            size = 36
        else:
            damage_per_frame = game.ship.damage
            color = (255, 200, 0)
            size = 24

        if not game.ship.hit:
            game.ship.damage_multiplier += 0.1
        damage_per_frame *= game.ship.damage_multiplier

        if game.ship.hit:
            game.ship.damage_multiplier = 1.0

        asteroid[0].hitpoints -= damage_per_frame
        x, y = asteroid[0].rect.center

        if not game.ship.hit:
            mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
            add_multiplier(game, mult_x, mult_y, f"x{game.ship.damage_multiplier:.2f}",
                                color=color, font_size=size)

        game.floating_numbers.add(
            FloatingNumber(x, y, int(damage_per_frame), color=color,
                           # type: ignore
                           font_size=size))
        impact = ImpactFrame(asteroid[0].rect.centerx,
                             asteroid[0].rect.centery,
                             game.frame_explode[0])
        game.explosions.add(impact)  # type: ignore
        for _ in range(10):
            vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
            game.particles.append(Particle(
                (asteroid[0].rect.centerx, asteroid[0].rect.centery), vel))
        if asteroid[0].hitpoints <= 0:
            asteroid[0].kill()
            game.ship.credits += random.randint(0, 5)
            if maniac_skill := next((s for s in game.skills.get_unlocked()
                                     if s.name == "Maniac"), None):
                maniac_skill.ability.apply(game.ship, maniac_skill.level)
            explosion = Explosion(asteroid[0].rect.centerx,
                                  asteroid[0].rect.centery,
                                  game.frame_explode)
            game.explosions.add(explosion)  # type: ignore
            if game.play_sound:
                game.sounds[1].play()
            game.score_multiplier = game.ship.damage_multiplier
            game.score += game.ship.level * 10 * game.score_multiplier
            game.ship.gain_xp(formulize(game, game.ship.level), game.sounds)

    hits2 = pg.sprite.groupcollide(game.projectiles, game.aliens, True,
                                   False)
    for alien in hits2.values():
        current_time = pg.time.get_ticks()
        if current_time > game.ship.maniac_boost_end:
            game.ship.maniac_boost = 0

        effective_crit_chance = min(1.0, (
                game.ship.crit_chance / 100) + game.ship.maniac_boost)
        if random.random() < effective_crit_chance:
            damage_per_frame = game.ship.damage * game.ship.crit_multiplier
            color = (255, 50, 50)
            size = 36
        else:
            damage_per_frame = game.ship.damage
            color = (255, 200, 0)
            size = 24

        if not game.ship.hit:
            game.ship.damage_multiplier += 0.1
        damage_per_frame *= game.ship.damage_multiplier

        if game.ship.hit:
            game.ship.damage_multiplier = 1.0

        alien[0].hitpoints -= damage_per_frame
        x, y = alien[0].rect.center

        if not game.ship.hit:
            mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
            add_multiplier(game, mult_x, mult_y,
                           f"x{game.ship.damage_multiplier:.2f}",
                                color=color, font_size=size)

        game.floating_numbers.add(
            FloatingNumber(x, y, int(damage_per_frame), color=color,
                           # type: ignore
                           font_size=size))
        impact = ImpactFrame(alien[0].rect.centerx, alien[0].rect.centery,
                             game.frame_explode[0])
        game.explosions.add(impact)  # type: ignore
        for _ in range(10):
            vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
            game.particles.append(
                Particle((alien[0].rect.centerx, alien[0].rect.centery),
                         vel))

        if alien[0].hitpoints <= 0:
            game.ship.credits += random.randint(0, 10)
            if maniac_skill := next((s for s in game.skills.get_unlocked()
                                     if s.name == "Maniac"), None):
                maniac_skill.ability.apply(game.ship, maniac_skill.level)
            explosion = Explosion(alien[0].rect.centerx,
                                  alien[0].rect.centery, game.frame_explode)
            game.explosions.add(explosion)  # type: ignore
            if game.play_sound:
                game.sounds[1].play()
            game.score_multiplier = game.ship.damage_multiplier
            game.score += game.ship.level * 10 * game.score_multiplier
            game.ship.gain_xp(formulize(game, game.ship.level), game.sounds)

    upgrade_hit = pg.sprite.spritecollide(game.ship, game.upgrades, False,
                                          # type: ignore
                                          collided=lambda s,
                                                          u: s.hitbox.colliderect(
                                              u.rect))
    if upgrade_hit:
        for upgrade in upgrade_hit:
            upgrade.kill()
            if game.play_sound:
                game.sounds[2].play()
            if game.last_upgrade == "power_up":
                game.active_upgrade = "power_up"
                game.upgrade_start_time = pg.time.get_ticks()
            elif game.last_upgrade == "shield":
                game.ship.shield = min(game.ship.shield + 10,
                                       game.ship.max_shield)