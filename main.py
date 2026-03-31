import pygame as pg
from pygame.display import toggle_fullscreen

from scripts import upgd
from scripts.asteroid import Asteroid
from scripts.celestial import *
from scripts.explode import Explosion
from scripts.proj import Projectile
from scripts.sheet import SpriteSheet
from scripts.ship import Ship
from scripts.soundlib import load_sounds, load_ost
from scripts.upgd import Upgrade


class Menu:
    def __init__(self):
        pg.init()
        pg.font.init()
        self.width = int(pg.display.Info().current_w)
        self.height = int(pg.display.Info().current_h)
        self.screen_size = (self.width, self.height)
        self.screen = pg.display.set_mode(self.screen_size, pg.SCALED, vsync=1)
        self.game_font = pg.font.Font("assets/ui/PressStart2P.ttf", 56)
        self.text_font = pg.font.Font("assets/ui/PressStart2P.ttf", 24)
        pg.display.set_caption("Astros")
        self.clock = pg.time.Clock()
        self.running = True
        self.cursor = False
        pg.mouse.set_visible(self.cursor)
        toggle_fullscreen()

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        game = Game(self.screen_size)
                        game.run(self.running, self.clock, self.screen,
                                 self.screen_size, self.text_font)
                    elif event.key == pg.K_ESCAPE:
                        self.running = False

            self.screen.fill((0, 0, 0))
            title = self.game_font.render("ASTROS", True, (255, 220, 50))
            start = self.text_font.render("Press Enter", True,"WHITE")
            title_y = 200
            self.screen.blit(title, (self.screen_size[0]//2 - title.get_width()//2, title_y))
            self.screen.blit(start, (self.screen_size[0]//2 - start.get_width()//2, title_y + 600))
            pg.display.update()
            self.clock.tick(60)

class Game:
    def __init__(self, screen_size):
        self.fps = 60
        self.frame = 0
        self.prev_state = None
        self.scale = 4
        self.sounds = load_sounds()
        self.theme = load_ost()
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(0.5)

        self.celestials = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.upgrades = pg.sprite.Group()

        self.cols = 12
        self.explosion_frames = 7
        self.sprite_sheet = SpriteSheet("assets/ship.png")
        self.explosion_sheet = SpriteSheet("assets/explosion.png")
        framew = self.sprite_sheet.sheet.get_width() // self.cols
        frameh = self.sprite_sheet.sheet.get_height()
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         framew, frameh, columns=self.cols)
        self.ship_alive = True
        self.ship_x = screen_size[0] // 2 - framew // 2 - 25
        self.ship_y = screen_size[1] // 2 + 200

        self.anim_frame_base = 0
        self.anim_frame_overlay = 0
        self.anim_index_left = 0
        self.anim_index_right = 0
        self.cooldown_base = 100
        self.cooldown_overlay = 50
        self.anim_base_index = 0
        self.anim_base_direction = 1
        self.cooldown_base = 100
        self.last_update_base = pg.time.get_ticks()
        self.last_update_overlay = pg.time.get_ticks()
        self.last_update = pg.time.get_ticks()
        self.last_update_left = pg.time.get_ticks()
        self.last_update_right = pg.time.get_ticks()
        self.last_direction = None
        self.frames = []
        for i in range(self.cols):
            img = self.sprite_sheet.get_image(i, framew, frameh, scale=self.scale,
                                              columns=self.cols)
            self.frames.append(img)

        self.left_frames_movement = self.frames[0:2]
        self.frame_idle = self.frames[2]
        self.right_frames_movement = self.frames[3:5]
        self.frames_flying = self.frames[5:9]
        self.frames_shooting = self.frames[9:12]

        framew = self.explosion_sheet.sheet.get_width() // self.explosion_frames
        frameh = self.explosion_sheet.sheet.get_height()
        self.frame_explode = [self.explosion_sheet.get_image(i, framew, frameh, scale=self.scale,
                                                            columns=self.explosion_frames)
                                                            for i in range(self.explosion_frames)]
        self.stars = [[random.randint(0, screen_size[0]),
                       random.randint(0, screen_size[1]),
                       random.randint(1, 3)] for _ in range(100)]
        self.last_celestial_spawn = 0
        self.celestial_spawn_interval = 10000
        self.last_asteroid_spawn = 0
        self.asteroid_spawn_interval = 800
        self.last_upgrade_spawn = 0
        self.upgrade_spawn_interval = 60_000
        self.last_shot_time = 0
        self.shot_cooldown = 300
        self.score = 0
        self.survival_bonus = 0
        self.game_over = False

        self.debugging = False
        self.cursor = True

    def run(self, running, clock, screen, screen_size, game_font):
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if self.game_over and event.key == pg.K_r:
                        self.reset(screen_size)
                    if event.key == pg.K_F2:
                        self.debug()

            clock.tick(self.fps)
            screen.fill((0,0,0))

            for i in self.stars:
                pg.draw.circle(screen, (255, 255, 255),
                                   (int(i[0]), int(i[1])), i[2])
                i[1] += 2
                if i[1] > screen_size[1]:
                    i[1] = 0
                    i[0] = random.randint(0, screen_size[0])

            current_time = pg.time.get_ticks()
            if current_time - self.last_asteroid_spawn > self.asteroid_spawn_interval:
                self.last_asteroid_spawn = current_time
                for _ in range(random.randint(1, 4)):
                    for _ in range(10):
                        new_asteroid = Asteroid(screen_size[0], min_y=-200, max_y=-50)
                        too_close = any(abs(new_asteroid.rect.y - m.rect.y) < 60 for m in self.asteroids)
                        if not too_close:
                            self.asteroids.add(new_asteroid) # type: ignore
                            break

            current_time = pg.time.get_ticks()
            if current_time - self.last_upgrade_spawn > self.upgrade_spawn_interval:
                self.last_upgrade_spawn = current_time
                new_upgrade = Upgrade(upgd.get_upgrade(), -200, -50)
                self.upgrades.add(new_upgrade) # type: ignore

            current_time = pg.time.get_ticks()
            if current_time - self.last_celestial_spawn > self.celestial_spawn_interval:
                self.last_celestial_spawn = current_time
                for _ in range(random.randint(1, 4)):
                    for _ in range(10):
                        new_celestial = random_celestial()
                        too_close = any(abs(new_celestial.rect.y - m.rect.y) < 120 for m in self.celestials)
                        if not too_close:
                            self.celestials.add(new_celestial) # type: ignore
                            break

            self.celestials.update()
            self.celestials.draw(screen)

            now = pg.time.get_ticks()
            if now - self.last_update_base > self.cooldown_base:
                self.anim_frame_base += 1
                self.last_update_base = now

            if now - self.last_update_overlay > self.cooldown_overlay:
                self.anim_frame_overlay += 1
                self.last_update_overlay = now

            if self.ship.direction in ["left", "right"]:
                if self.ship.direction == "left":
                    frames = self.left_frames_movement
                    if self.last_direction != "left":
                        self.anim_index_left = 0
                        self.last_update_left = pg.time.get_ticks()
                        self.last_direction = "left"

                    if pg.time.get_ticks() - self.last_update_left > self.cooldown_base:
                        self.anim_index_left += 1
                        if self.anim_index_left >= len(frames):
                            self.anim_index_left = len(frames) - 1
                        self.last_update_left = pg.time.get_ticks()

                    base = frames[self.anim_index_left]

                else:
                    frames = self.right_frames_movement
                    if self.last_direction != "right":
                        self.anim_index_right = 0
                        self.last_update_right = pg.time.get_ticks()
                        self.last_direction = "right"

                    if pg.time.get_ticks() - self.last_update_right > self.cooldown_base:
                        self.anim_index_right += 1
                        if self.anim_index_right >= len(frames):
                            self.anim_index_right = len(frames) - 1
                        self.last_update_right = pg.time.get_ticks()
                    base = frames[self.anim_index_right]
            else:
                base = self.frame_idle
                self.last_direction = None
            img = base.copy()

            if self.ship.moving:
                overlay_index = self.anim_frame_overlay % len(
                    self.frames_flying)
                overlay_frame = self.frames_flying[overlay_index]
                img.blit(overlay_frame, (0, 0))

            if self.ship.shooting:
                shoot_index = self.anim_frame_overlay % len(
                    self.frames_shooting)
                shoot_frame = self.frames_shooting[shoot_index]
                img.blit(shoot_frame, (0, 0))

            self.asteroids.update()
            self.asteroids.draw(screen)

            if self.debugging:
                for i in self.asteroids:
                    pg.draw.rect(screen, (255, 0, 0),i.hitbox, 2)

            if self.ship_alive:
                self.ship.rect.topleft = (self.ship_x, self.ship_y)
                screen.blit(img, self.ship.rect)
                if self.debugging:
                    pg.draw.rect(screen, (255, 0, 0), self.ship.hitbox,2)

            if not self.game_over:
                self.upgrades.update()
                self.upgrades.draw(screen)

                key_pressed = pg.key.get_pressed()
                self.ship.moving = False
                self.ship.direction = "idle"

                if key_pressed[pg.K_LEFT] and self.ship_x > 0:
                    self.ship_x -= self.ship.velocity
                    self.ship.direction = "left"
                    self.ship.moving = True
                if key_pressed[pg.K_RIGHT] and self.ship_x < screen_size[
                    0] - img.get_width():
                    self.ship_x += self.ship.velocity
                    self.ship.direction = "right"
                    self.ship.moving = True
                if key_pressed[pg.K_UP] and self.ship_y > 0:
                    self.ship_y -= self.ship.velocity
                    self.ship.moving = True
                if key_pressed[pg.K_DOWN] and self.ship_y < screen_size[
                    1] - self.ship.image.get_height():
                    self.ship_y += self.ship.velocity

                if self.ship_alive:
                    self.ship.shooting = False
                    if key_pressed[
                        pg.K_SPACE] and current_time - self.last_shot_time >= self.shot_cooldown:
                        self.last_shot_time = current_time
                        self.ship.shooting = True
                        projectile = Projectile(self.ship_x + img.get_width() // 2,self.ship_y)
                        self.projectiles.add(projectile) # type: ignore
                        self.sounds[0].play()

                self.projectiles.update()
                self.projectiles.draw(screen)

                if self.ship_alive:
                    self.ship.update_position(self.ship_x, self.ship_y)
                asteroid_hit = pg.sprite.spritecollideany(self.ship, self.asteroids,  # type: ignore
                                                        collided=lambda s, m:
                                                            s.hitbox.colliderect(m.hitbox))
                if asteroid_hit and not self.game_over:
                    ship_center_x = self.ship.rect.centerx
                    ship_center_y = self.ship.rect.centery
                    explosion = Explosion(ship_center_x, ship_center_y, self.frame_explode)
                    self.explosions.add(explosion) # type: ignore
                    asteroid_hit.kill()
                    self.sounds[1].play()
                    self.ship.kill()
                    self.ship_alive = False

                    pg.mixer.music.stop()
                    self.game_over = True

                hits = pg.sprite.groupcollide(self.projectiles,
                                              self.asteroids,
                                              True, False)
                for asteroid in hits.values():
                    explosion = Explosion(asteroid[0].rect.centerx,
                                          asteroid[0].rect.centery,
                                          self.frame_explode)
                    self.explosions.add(explosion) # type: ignore
                    asteroid[0].kill()
                    self.sounds[1].play()
                    self.score += 10

                upgrade_hit = pg.sprite.spritecollide(self.ship, self.upgrades,False,  # type: ignore
                                                      collided=lambda s,u: s.hitbox.colliderect(u.rect))
                if upgrade_hit:
                    for upgrade in upgrade_hit:
                        upgrade.kill()

                self.survival_bonus += 1
                if self.survival_bonus >= 60:
                    self.survival_bonus = 0
                    self.score += 1

            self.explosions.update()
            self.explosions.draw(screen)

            score_text = f"{self.score:05}"
            text_surface = game_font.render(score_text, True, "WHITE")
            screen.blit(text_surface, [screen_size[0] - 160, 50])
            pg.display.update()

            if self.game_over:
                game_over = game_font.render("GAME OVER", True, "RED")
                screen.blit(game_over,[screen_size[0] // 2 - 150, screen_size[1] // 2])

        pg.quit()

    def reset(self, screen_size):
        self.projectiles.empty()
        self.asteroids.empty()
        self.explosions.empty()
        framew = self.sprite_sheet.sheet.get_width() // self.cols
        frameh = self.sprite_sheet.sheet.get_height()
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         framew, frameh, columns=self.cols)
        self.ship_alive = True
        self.ship_x = screen_size[0] // 2 - framew // 2 - 25
        self.ship_y = screen_size[1] // 2 + 200

        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.last_asteroid_spawn = 0
        self.last_shot_time = 0
        self.score = 0
        self.game_over = False
        pg.mixer.music.play(-1)

    def debug(self):
        if self.debugging:
            self.debugging = False
            return

        if not self.debugging:
            self.debugging = True
            return

if __name__ == '__main__':
    menu = Menu()
    menu.run()