import random

import pygame

from scripts.explode import Explosion
from scripts.floaty import FloatingNumber
from scripts.impact import ImpactFrame
from scripts.particle import Particle
from scripts.toggles import invincible
from scripts.utils import add_multiplier, formulize


def check_collision(game):
    if game.state.current_phase in [game.state.phases[3], game.state.phases[5]]:
        asteroid_hit = pygame.sprite.spritecollideany(game.ship, game.asteroids, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.hitbox))
    else:
        asteroid_hit = None

    if game.state.current_phase in game.state.phases:
        alien_hit = pygame.sprite.spritecollideany(game.ship, game.aliens, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.hitbox))
    else:
        alien_hit = None

    if game.state.current_phase in game.state.phases:
        alien_proj = pygame.sprite.spritecollideany(game.ship, game.enemy_projectiles, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.rect))
    else:
        alien_proj = None

    if asteroid_hit or alien_hit or alien_proj:
        if random.random() <= game.ship.evasion:
            if asteroid_hit:
                x, y = asteroid_hit.rect.center
                game.floating_numbers.add(FloatingNumber(
                    x, y, "MISS", color=(255, 255, 100)))
            elif alien_hit:
                x, y = alien_hit.rect.center
                game.floating_numbers.add(FloatingNumber(
                    x, y, "MISS", color=(255, 255, 100)))
            elif alien_proj:
                x, y = alien_proj.rect.center
                game.floating_numbers.add(FloatingNumber(
                    x, y, "MISS", color=(255, 255, 100)))
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
        if not invincible:
            if game.ship.shield > 0:
                damage_per_frame = (max(1,game.ship.max_shield // 33) * game.ship.level)
                game.ship.shield -= damage_per_frame
            else:
                damage_per_frame = max(1,game.ship.max_hitpoints // 28) * game.ship.level
                game.ship.hitpoints -= damage_per_frame

        if hasattr(game.ship, "fortified_percent"):
            if game.ship.fortified_percent > 0:
                shield_gain = int(damage_per_frame * game.ship.fortified_percent)
                if hasattr(game.ship, "fortified_cap"):
                    shield_gain = min(shield_gain, game.ship.fortified_cap)
                game.ship.shield += shield_gain

        game.screen_shake = 20

        if game.ship.hitpoints <= 0:
            game.state.game_over = True
            game.ship.kill()
            game.ship_alive = False
            pygame.mixer.music.stop()
            game.state.game_over = True

    hits1 = pygame.sprite.groupcollide(game.projectiles, game.asteroids, True,
                                   False)
    for projectile, asteroids_hit in hits1.items():
        for asteroid in asteroids_hit:
            current_time = pygame.time.get_ticks()
            if current_time > game.ship.maniac_boost_end:
                game.ship.maniac_boost = 0

            effective_crit_chance = min(1.0, (game.ship.crit_chance / 100) + game.ship.maniac_boost)
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

            asteroid.hitpoints -= damage_per_frame
            x, y = asteroid.rect.center

            if not game.ship.hit:
                mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
                add_multiplier(game, mult_x, mult_y,
                               f"x{game.ship.damage_multiplier:.2f}",
                               color=color, font_size=size)

            game.floating_numbers.add(
                FloatingNumber(x, y, int(damage_per_frame), color=color,
                               font_size=size))
            impact = ImpactFrame(asteroid.rect.centerx, asteroid.rect.centery,
                                 game.frame_explode[0])
            game.explosions.add(impact)
            for _ in range(10):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                game.particles.append(
                    Particle((asteroid.rect.centerx, asteroid.rect.centery),
                             vel))

            if asteroid.hitpoints <= 0:
                asteroid.kill()
                game.ship.credits += random.randint(1, 50)
                if maniac_skill := next(
                        (s for s in game.skills.get_unlocked() if
                         s.name == "Maniac"), None):
                    maniac_skill.ability.apply(game.ship, maniac_skill.level)
                explosion = Explosion(asteroid.rect.centerx,
                                      asteroid.rect.centery, game.frame_explode)
                game.explosions.add(explosion)
                if game.play_sound:
                    game.sounds[1].play()
                game.state.score_multiplier = game.ship.damage_multiplier
                game.score += game.ship.level * 10 * game.state.score_multiplier
                game.ship.gain_xp(formulize(game, game.ship.level), game.sounds)

    hits2 = pygame.sprite.groupcollide(game.projectiles, game.aliens, True, False)
    for projectile, aliens_hit in hits2.items():
        for alien in aliens_hit:
            current_time = pygame.time.get_ticks()
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

            alien.hitpoints -= damage_per_frame
            x, y = alien.rect.center

            if not game.ship.hit:
                mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
                add_multiplier(game, mult_x, mult_y,
                               f"x{game.ship.damage_multiplier:.2f}",
                               color=color, font_size=size)

            game.floating_numbers.add(FloatingNumber(x, y, int(damage_per_frame), color=color,
                               font_size=size))
            impact = ImpactFrame(alien.rect.centerx, alien.rect.centery,
                                 game.frame_explode[0])
            game.explosions.add(impact)
            for _ in range(10):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                game.particles.append(
                    Particle((alien.rect.centerx, alien.rect.centery), vel))

            if alien.hitpoints <= 0:
                alien.kill()
                game.ship.credits += random.randint(1, 100)
                if maniac_skill := next(
                        (s for s in game.skills.get_unlocked() if
                         s.name == "Maniac"), None):
                    maniac_skill.ability.apply(game.ship, maniac_skill.level)
                explosion = Explosion(alien.rect.centerx, alien.rect.centery,
                                      game.frame_explode)
                game.explosions.add(explosion)
                if game.play_sound:
                    game.sounds[1].play()
                game.state.score_multiplier = game.ship.damage_multiplier
                game.state.score += (game.ship.level * 10 * game.state.score_multiplier)
                game.ship.gain_xp(formulize(game, game.ship.level), game.sounds)

    hits3 = pygame.sprite.groupcollide(game.projectiles, game.bosses, True, False)
    for projectile, boss_hit in hits3.items():
        for boss in boss_hit:
            current_time = pygame.time.get_ticks()
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

            boss.hitpoints -= damage_per_frame
            x, y = boss.rect.center

            if not game.ship.hit:
                mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
                add_multiplier(game, mult_x, mult_y,
                               f"x{game.ship.damage_multiplier:.2f}",
                               color=color, font_size=size)

            game.floating_numbers.add(
                FloatingNumber(x, y, int(damage_per_frame), color=color,
                               font_size=size))
            impact = ImpactFrame(boss.rect.centerx, boss.rect.centery,
                                 game.frame_explode[0])
            game.explosions.add(impact)
            for _ in range(10):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                game.particles.append(
                    Particle((boss.rect.centerx, boss.rect.centery), vel))

            if boss.hitpoints <= 0:
                boss.kill()
                game.ship.credits += random.randint(1, 100)
                if maniac_skill := next(
                        (s for s in game.skills.get_unlocked() if
                         s.name == "Maniac"), None):
                    maniac_skill.ability.apply(game.ship, maniac_skill.level)
                explosion = Explosion(boss.rect.centerx, boss.rect.centery,
                                      game.frame_explode)
                game.explosions.add(explosion)
                if game.play_sound:
                    game.sounds[1].play()
                game.state.score_multiplier = game.ship.damage_multiplier
                game.score += game.ship.level * 10 * game.state.score_multiplier
                game.ship.gain_xp(formulize(game, game.ship.level), game.sounds)

    upgrade_hit = pygame.sprite.spritecollide(game.ship, game.upgrades, False, # type: ignore
                                          collided=lambda s,u: s.hitbox.colliderect(u.rect))
    if upgrade_hit:
        for upgrade in upgrade_hit:
            upgrade.kill()
            if game.play_sound:
                game.sounds[2].play()
            if game.last_upgrade == "power_up":
                game.active_upgrade = "power_up"
                game.upgrade_start_time = pygame.time.get_ticks()
            elif game.last_upgrade == "shield":
                game.ship.shield = min(game.ship.shield + 10,
                                       game.ship.max_shield)