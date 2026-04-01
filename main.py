import pygame as pg
from pygame.constants import OPENGL, DOUBLEBUF
from pygame.display import toggle_fullscreen

from scripts import upgd
from scripts.asteroid import Asteroid
from scripts.celestial import *
from scripts.crt import CRT
from scripts.explode import Explosion
from scripts.hud import Interface
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
        self.hud_padding = 100
        self.hud_ratio = Game.set_hud(self.screen_size, self.hud_padding)
        self.virtual_screen = pg.display.set_mode(self.screen_size)
        self.render_surface = pg.Surface((1920, 1080))
        self.screen = pg.display.set_mode(self.screen_size, DOUBLEBUF|OPENGL, vsync=1)
        self.crt = CRT(self.screen, style=1, virtual_resolution=(1920, 1080),cpu_only=False)
        self.crt.prog['curvature'].value = 0.7
        self.font = "assets/ui/PressStart2P.ttf"
        self.cursor_sprite = pg.image.load("assets/ui/cursor.png")
        self.game_font = pg.font.Font(self.font, 80)
        self.text_font = pg.font.Font(self.font, 24)
        pg.display.set_caption("Astros")
        self.clock = pg.time.Clock()
        self.running = True
        pg.mouse.set_visible(False)
        toggle_fullscreen()

    def run(self):
        count = 0
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        game = Game(self.screen_size, self.hud_ratio)
                        game.run(self.running, self.clock, self.screen, self.screen_size,
                                 self.hud_padding, self.hud_ratio, self.crt, self.text_font)
                    elif event.key == pg.K_ESCAPE:
                        self.running = False

            self.screen.fill((0, 0, 0))

            colors = ["WHITE", (0,0,0,0)]
            count += 1
            title = self.game_font.render("ASTROS", True, (255, 220, 50))
            start = self.text_font.render("Press Enter", True, colors[count%2])
            title_y = 200
            self.render_surface.fill((0, 0, 0))
            surface_width, surface_height = self.render_surface.get_size()
            title_x = surface_width // 2 - title.get_width() // 2
            start_x = surface_width // 2 - start.get_width() // 2
            self.render_surface.blit(title, (title_x, title_y))
            self.render_surface.blit(start, (start_x, title_y + 600))
            self.screen.blit(pg.transform.scale(self.render_surface, self.screen_size),(0, 0))
            self.crt.render(self.render_surface)
            self.clock.tick(2)

class Game:
    def __init__(self, screen_size, hud_ratio):
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
        self.base = None
        self.hud = Interface(0, 40, 40,hud_ratio)

        self.anim_frame_base = 0
        self.anim_frame_overlay = 0
        self.anim_index_left = 0
        self.anim_index_right = 0
        self.cooldown_base = 100
        self.cooldown_overlay = 50
        self.anim_base_index = 0
        self.anim_base_direction = 1

        self.last_update_base = pg.time.get_ticks()
        self.last_update_overlay = pg.time.get_ticks()
        self.last_update = pg.time.get_ticks()
        self.last_update_left = pg.time.get_ticks()
        self.last_update_right = pg.time.get_ticks()
        self.last_direction = None
        self.last_time = pg.time.get_ticks()

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
        self.celestial_spawn_interval = random.randint(8000, 14000)
        self.last_asteroid_spawn = 0
        self.asteroid_spawn_interval = 800
        self.asteroid_spawn_count = 4
        self.last_upgrade_spawn = 0
        self.upgrade_spawn_interval = 60_000
        self.last_shot_time = 0
        self.shot_cooldown = 300
        self.score = 0
        self.high_score = 0
        self.survival_bonus = 0
        self.game_over = False

        self.play_sound = True
        self.pause = False
        self.debugging = False
        self.cursor = True

        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.milliseconds = 0
        self.stopwatch = None

        self.screen_shake = 0
        self.count = 0
        self.last_blink = 0

        self.cursor_sprite = pg.image.load("assets/ui/cursor.png").convert_alpha()
        self.cursor_visible = False
        self.last_cursor_pos = pg.mouse.get_pos()
        self.last_move_time = pg.time.get_ticks()
        self.cursor_hide_delay = 3000

    def run(self, running, clock, screen,
            screen_size, hud_padding, hud_ratio, crt, font):
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        if event.mod & pg.KMOD_SHIFT:
                            crt.prog['curvature'].value = max(0.0,
                            crt.prog['curvature'].value - 0.5)
                        else:
                            crt.prog['curvature'].value += 0.5
                    if event.key == pg.K_KP_PLUS:
                        hud_padding += 5
                        hud_ratio = Game.set_hud(screen_size, hud_padding)
                    if event.key == pg.K_KP_MINUS:
                        hud_padding -= 5
                        if hud_padding < 0:
                            hud_padding = 0
                        hud_ratio = Game.set_hud(screen_size, hud_padding)

                    if self.game_over and event.key == pg.K_r:
                        self.reset(screen_size)
                    if event.key == pg.K_F2:
                        self.debug()
                    if event.key == pg.K_ESCAPE:
                        self.pause = not self.pause
                    if event.key == pg.K_q and (event.mod & pg.KMOD_CTRL):
                        running = False

            if not running:
                break

            clock.tick(self.fps)
            screen.fill((0,0,0))

            mouse_pos = pg.mouse.get_pos()
            if mouse_pos != self.last_cursor_pos:
                self.last_cursor_pos = mouse_pos
                self.last_move_time = pg.time.get_ticks()
                self.cursor_visible = True

            if pg.time.get_ticks() - self.last_move_time > self.cursor_hide_delay:
                self.cursor_visible = False

            if not self.pause and not self.game_over:
                for i in self.stars:
                    if not self.pause:
                        i[1] += 2
                    if i[1] > screen_size[1]:
                        i[1] = 0
                        i[0] = random.randint(0, screen_size[0])

                current_time = pg.time.get_ticks()
                if current_time - self.last_celestial_spawn > self.celestial_spawn_interval:
                    self.last_celestial_spawn = current_time
                    for _ in range(random.randint(1, 4)):
                        for _ in range(10):
                            new_celestial = random_celestial()
                            if new_celestial and is_valid_spawn(new_celestial,
                                                                self.celestials,
                                                                200):
                                self.celestials.add(new_celestial)
                                break

                current_time = pg.time.get_ticks()
                if current_time - self.last_upgrade_spawn > self.upgrade_spawn_interval:
                    for _ in range(random.randint(1, 2)):
                        for _ in range(5):
                            self.last_upgrade_spawn = current_time
                            new_upgrade = Upgrade(upgd.get_upgrade(), -200, -50)
                            self.upgrades.add(new_upgrade) # type: ignore

                current_time = pg.time.get_ticks()
                if current_time - self.last_asteroid_spawn > self.asteroid_spawn_interval:
                    self.last_asteroid_spawn = current_time
                    for _ in range(random.randint(1, self.asteroid_spawn_count)):
                        for _ in range(10):
                            new_asteroid = Asteroid(screen_size[0], min_y=-200, max_y=-50)
                            too_close = any(abs(new_asteroid.rect.y - m.rect.y) < 60 for m in self.asteroids)
                            if not too_close:
                                self.asteroids.add(new_asteroid)  # type: ignore
                                break

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
                            self.last_update_left = now
                            self.last_direction = "left"

                        if now - self.last_update_left > self.cooldown_base:
                            self.anim_index_left += 1
                            if self.anim_index_left >= len(frames):
                                self.anim_index_left = len(frames) - 1
                            self.last_update_left = now
                        self.base = frames[self.anim_index_left]
                    else:
                        frames = self.right_frames_movement
                        if self.last_direction != "right":
                            self.anim_index_right = 0
                            self.last_update_right = now
                            self.last_direction = "right"

                        if now - self.last_update_right > self.cooldown_base:
                            self.anim_index_right += 1
                            if self.anim_index_right >= len(frames):
                                self.anim_index_right = len(frames) - 1
                            self.last_update_right = now
                        self.base = frames[self.anim_index_right]
                else:
                    self.base = self.frame_idle

                self.celestials.update()
                self.asteroids.update()
                self.projectiles.update()
                self.explosions.update()
                self.upgrades.update()

                key_pressed = pg.key.get_pressed()
                self.ship.moving = False
                direction_set = False
                if key_pressed[pg.K_LEFT] and self.ship_x > 0:
                    self.ship_x -= self.ship.velocity
                    self.ship.direction = "left"
                    self.ship.moving = True
                    direction_set = True
                elif (key_pressed[pg.K_RIGHT] and self.ship_x < screen_size[0]
                      - self.base.copy().get_width()):
                    self.ship_x += self.ship.velocity
                    self.ship.direction = "right"
                    self.ship.moving = True
                    direction_set = True
                if key_pressed[pg.K_UP] and self.ship_y > 0:
                    self.ship_y -= self.ship.velocity
                    self.ship.moving = True
                if key_pressed[pg.K_DOWN] and self.ship_y < screen_size[1] - self.ship.image.get_height():
                    self.ship_y += self.ship.velocity

                if not direction_set:
                    self.ship.direction = "idle"

                if self.ship_alive:
                    self.ship.shooting = False
                    if key_pressed[pg.K_SPACE] and current_time - self.last_shot_time >= self.shot_cooldown:
                        self.last_shot_time = current_time
                        self.ship.shooting = True
                        projectile = Projectile(self.ship_x + self.base.copy().get_width() // 2, self.ship_y)
                        self.projectiles.add(projectile) # type: ignore
                        if self.play_sound:
                            self.sounds[0].play()

                if key_pressed[pg.K_m]:
                    self.play_sound = not self.play_sound

                if self.ship_alive:
                    self.ship.update_position(self.ship_x, self.ship_y)
                asteroid_hit = pg.sprite.spritecollideany(self.ship, self.asteroids,  # type: ignore
                                                        collided=lambda s, m:s.hitbox.colliderect(m.hitbox))
                if asteroid_hit:
                    ship_center_x = self.ship.rect.centerx
                    ship_center_y = self.ship.rect.centery
                    explosion = Explosion(ship_center_x, ship_center_y, self.frame_explode)
                    self.explosions.add(explosion) # type: ignore
                    asteroid_hit.kill()
                    if self.play_sound:
                        self.sounds[1].play()
                    self.ship.hitpoints -= self.ship.max_hitpoints // 28
                    self.screen_shake = 20
                    if self.ship.hitpoints <= 0:
                        self.game_over = True
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
                    if self.play_sound:
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

                self.update_time()

            for i in self.stars:
                pg.draw.circle(screen, (255, 255, 255), (int(i[0]), int(i[1])),i[2])

            self.celestials.draw(screen)
            self.asteroids.draw(screen)
            self.projectiles.draw(screen)
            self.upgrades.draw(screen)
            img = self.base.copy()
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

            if self.debugging:
                for i in self.asteroids:
                    pg.draw.rect(screen, (255, 0, 0), i.hitbox, 2)

            if self.ship_alive:
                self.ship.rect.topleft = (self.ship_x, self.ship_y)
                screen.blit(img, self.ship.rect)
                if self.debugging:
                    pg.draw.rect(screen, (255, 0, 0), self.ship.hitbox, 2)

            self.explosions.draw(screen)

            if not self.game_over:
                self.stopwatch = font.render(f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}",
                    True, "WHITE")
                screen.blit(self.stopwatch, [hud_ratio['left'] + hud_ratio['width'] // 2 -
                    self.stopwatch.get_width() // 2, hud_ratio['top']])

                total_frames = len(self.hud.frames) - 1
                if self.ship.hitpoints <= 0:
                    hitpoints_frame = total_frames
                else:
                    hitpoints_frame = (total_frames - (self.ship.hitpoints * total_frames)
                                       // self.ship.max_hitpoints)

                score_text = f"{self.score:05}"
                high_score = f"{self.high_score:05}"
                score_title = "SCORE"
                high_score_title = "HIGH\nSCORE"

                score_surface = font.render(score_text, True, "WHITE")
                score_title_surface = font.render(score_title, True, "WHITE")
                high_score_surfaces = [ font.render(line, True, "WHITE")
                    for line in high_score_title.split('\n')]
                high_score_surface = font.render(high_score, True, "WHITE")

                score_x = hud_ratio['left']
                score_y = hud_ratio['top']
                screen.blit(score_title_surface, [score_x,score_y - score_title_surface.get_height() - 5])
                screen.blit(score_surface, [score_x, score_y])

                y_pos = hud_ratio['top']
                x_pos = hud_ratio['right'] - max(s.get_width()
                    for s in high_score_surfaces + [high_score_surface])
                for line_surf in high_score_surfaces:
                    screen.blit(line_surf, [x_pos, y_pos])
                    y_pos += line_surf.get_height() + 2
                screen.blit(high_score_surface, [x_pos, y_pos])
                self.hud.update(self.ship, hud_ratio, hitpoints_frame, screen)

            if self.cursor_visible:
                screen.blit(self.cursor_sprite, mouse_pos)

            if self.game_over:
                now = pg.time.get_ticks()
                if now - self.last_blink > 500:
                    self.count += 1
                    self.last_blink = now

                colors = ["RED", (0,0,0,0)]
                game_over = font.render("GAME OVER", True, colors[self.count%2])

                if self.score > self.high_score:
                    self.high_score = self.score

                score_text = font.render(f"{self.score:05}", True, "WHITE")
                stopwatch = self.stopwatch
                game_over_x = self.center(game_over, screen_size)
                game_over_y = screen_size[1]// 2
                screen.blit(game_over,[game_over_x, game_over_y])
                screen.blit(score_text, [self.center(score_text, screen_size), game_over_y + 25])
                screen.blit(stopwatch, [self.center(stopwatch, screen_size), game_over_y + 50])

            if self.screen_shake > 0:
                self.screen_shake -= 1

            render = [0,0]
            if self.screen_shake:
                render = self.ship.taken_damage()
            if not self.game_over:
                screen.blit(pg.transform.scale(screen, screen_size), render)
            crt.render(screen)
        pg.quit()

    @staticmethod
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

    def update_time(self):
        current_time = pg.time.get_ticks()
        elapsed = current_time - getattr(self, 'last_time', 0)
        if not hasattr(self, 'last_time'):
            self.last_time = current_time
            return

        self.milliseconds += elapsed
        self.last_time = current_time

        if self.milliseconds >= 1000:
            self.milliseconds -= 1000
            self.seconds += 1

            if self.seconds % 48 == 0:
                self.asteroid_spawn_interval = max(100, self.asteroid_spawn_interval - 10)
                self.asteroid_spawn_count = min(32,self.asteroid_spawn_count + 1)
                self.ship.velocity = min(24, self.ship.velocity + 1)

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
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.milliseconds = 0
        self.stopwatch = None
        self.game_over = False
        if self.play_sound:
            pg.mixer.music.play(-1)

    def debug(self):
        if self.debugging:
            self.debugging = False
            return

        if not self.debugging:
            self.debugging = True
            return

    def center(self, text, screen_size):
        return screen_size[0] // 2 - text.get_width() // 2

if __name__ == '__main__':
    menu = Menu()
    menu.run()