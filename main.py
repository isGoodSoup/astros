import pygame as pg
from pygame.constants import *
from pygame.display import toggle_fullscreen

from scripts import upgd
from scripts.asteroid import Asteroid
from scripts.celestial import *
from scripts.crt import CRT
from scripts.explode import Explosion
from scripts.fade import Fade
from scripts.floaty import FloatingNumber
from scripts.hud import Interface
from scripts.impact import ImpactFrame
from scripts.particle import Particle
from scripts.sheet import SpriteSheet
from scripts.ship import Ship
from scripts.skill import SkillManager
from scripts.skill_tab import Tab
from scripts.soundlib import load_sounds, load_ost
from scripts.tutorial import Tutorial
from scripts.upgd import Upgrade

pg.joystick.init()
joysticks = [pg.joystick.Joystick(i) for i in range(pg.joystick.get_count())]
for j in joysticks: j.init()
if joysticks:
    controller = joysticks[0]

fade = Fade()

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
        self.logo_img = pygame.image.load("assets/ui/logo.png")
        self.logo_img = pygame.transform.scale(self.logo_img,
            (self.logo_img.get_width() * 4, self.logo_img.get_height() * 4))
        self.cursor_sprite = pg.image.load("assets/ui/cursor.png")
        self.game_font = pg.font.Font(self.font, 96)
        self.text_font = pg.font.Font(self.font, 24)
        pg.display.set_caption("Astros")
        self.clock = pg.time.Clock()
        self.sounds = load_sounds()
        self.running = True
        self.transitioning = False
        self.count = 0
        self.last_blink = 0
        pg.mouse.set_visible(False)
        toggle_fullscreen()

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN and not self.transitioning:
                        self.sounds[2].play()
                        fade.start("out")
                        self.transitioning = True
                elif event.type == JOYBUTTONDOWN:
                    if event.button in range(0, 9):
                        self.sounds[2].play()
                        fade.start("out")
                        self.transitioning = True

            alpha = fade.update()
            self.screen.fill((0, 0, 0))

            now = pg.time.get_ticks()
            if now - self.last_blink > 500:
                self.count += 1
                self.last_blink = now

            colors = [(255, 255, 255), (0, 0, 0, 0)]
            start = self.text_font.render("Press any key to start", True,
                                          colors[self.count % 2])
            title_y = 200
            self.render_surface.fill((0, 0, 0))
            surface_width, surface_height = self.render_surface.get_size()
            title_x = surface_width // 2 - self.logo_img.get_width() // 2
            start_x = surface_width // 2 - start.get_width() // 2
            self.render_surface.blit(self.logo_img, (title_x, title_y))
            self.render_surface.blit(start, (start_x, title_y + 600))
            self.screen.blit(pg.transform.scale(self.render_surface, self.screen_size),(0, 0))
            if alpha > 0:
                fade_surface = pg.Surface((1920, 1080))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                self.render_surface.blit(fade_surface, (0, 0))

            self.crt.render(self.render_surface)
            dt = self.clock.tick(60) / 1000

            if self.transitioning and not fade.active:
                self.init_game()
                return

    def init_game(self):
        game = Game(self.screen, self.screen_size,
                    self.hud_ratio, self.text_font)
        game.run(self.running, self.clock, self.screen,
                 self.screen_size, self.hud_padding,
                 self.hud_ratio, self.crt, self.text_font)

class Game:
    def __init__(self, screen, screen_size, hud_ratio,
                 game_font):
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
        self.floating_numbers = pg.sprite.Group()
        self.particles = []

        self.cols = 9
        self.explosion_frames = 7
        self.destroy_all = False
        self.sprite_sheet = SpriteSheet("assets/ship.png")
        self.explosion_sheet = SpriteSheet("assets/explosion.png")
        self.megaexplosion_sheet = SpriteSheet("assets/explosion_charge.png")
        framew = self.sprite_sheet.sheet.get_width() // self.cols
        frameh = self.sprite_sheet.sheet.get_height()
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         framew, frameh, columns=self.cols)
        self.ship_alive = True
        self.ship_x = screen_size[0] // 2 - framew // 2 - 25
        self.ship_y = screen_size[1] // 2 + 200
        self.ship_pos = [self.ship_x, self.ship_y]
        self.joy_axis = [0.0, 0.0]
        self.deadzone = 0.2

        self.hitpoints = Interface("assets/ui/status.png", 0, 40, 40,
            hud_ratio, ['right', 'bottom'])
        self.shield = Interface("assets/ui/shield_bar.png", 0, 40, 17,
            hud_ratio, ['right', 'bottom'], 33, [0, -150])
        self.xp = Interface("assets/ui/xp.png", -1, 40, 17,
            hud_ratio, ['right', 'bottom'], 33, [0,-175])
        self.ammo = Interface("assets/ui/ammo.png", 0, 11, 40,
            hud_ratio, ['right', 'bottom'], 35, [-160, 0])

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
        self.direction_set = None

        self.frames = []
        for i in range(self.cols):
            img = self.sprite_sheet.get_image(i, framew, frameh, scale=self.scale,columns=self.cols)
            self.frames.append(img)

        self.left_frames_movement = self.frames[0:2]
        self.frame_idle = self.frames[2]
        self.right_frames_movement = self.frames[3:5]
        self.frames_flying = self.frames[5:9]
        self.base = self.frame_idle

        framew = self.explosion_sheet.sheet.get_width() // self.explosion_frames
        frameh = self.explosion_sheet.sheet.get_height()
        self.frame_explode = [self.explosion_sheet.get_image(i, framew, frameh, scale=self.scale,
                                                            columns=self.explosion_frames)
                                                            for i in range(self.explosion_frames)]

        framew = self.megaexplosion_sheet.sheet.get_width() // 4
        frameh = self.megaexplosion_sheet.sheet.get_height()
        self.frame_big_explode = [self.megaexplosion_sheet.get_image(i, framew, frameh,
            scale=self.scale, columns=4) for i in range(4)]

        self.stars = [[random.randint(0, screen_size[0]),
                       random.randint(0, screen_size[1]),
                       random.randint(1, 3)] for _ in range(100)]
        self.last_celestial_spawn = 0
        self.celestial_spawn_interval = random.randint(8000, 14000)
        self.last_asteroid_spawn = 0
        self.asteroid_spawn_interval = 600
        self.asteroid_spawn_count = 6
        self.last_upgrade_spawn = 0
        self.upgrade_spawn_interval = 24_000
        self.last_shot_time = 0
        self.last_upgrade = None
        self.active_upgrade = None
        self.upgrade_start_time = 0
        self.upgrade_duration = 16_000

        self.charge_active = False
        self.charge_start_time = 0
        self.charge_duration = 2000
        self.charge_rumble = 0.3

        self.score = 0
        self.score_multiplier = 1.0
        self.high_score = 0
        self.active_mults = []
        self.survival_bonus = 0
        self.game_over = False

        self.skill_tab = Tab(
            "assets/ui/skill_tab.png",
            start_pos=(screen_size[0], 200),
            content_renderer=self.render_skills_tab
        )
        self.skill_tab.set_target(
            (screen_size[0] - self.skill_tab.width - 100, 200))

        self.stats_tab = Tab(
            "assets/ui/skill_tab.png",
            start_pos=(100, screen_size[1]),
            content_renderer=self.render_stats_tab
        )
        self.stats_tab.set_target(
            (100, screen_size[1] - self.stats_tab.height - 100))
        self.skills = SkillManager()
        self.skills.build_tree(self.skill_tab)

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
        
        self.tutorial_on = False
        if self.tutorial_on:
            self.tutorial = Tutorial()

        self.delay = 99_999

        self.game_over_fx = True
        fade.start("in")

    def run(self, running, clock, screen,
            screen_size, hud_padding, hud_ratio, crt, font):
        clock.tick()
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        self.skill_tab.active = not self.skill_tab.active
                        self.stats_tab.active = not self.stats_tab.active

                    if event.key == pg.K_f:
                        if self.ship.charges > 0:
                            self.ship.super_charge(joysticks, self.score,self.explosions,
                                                   self.asteroids, self.frame_explode, self.frame_big_explode)
                            self.screen_shake = 50
                    if event.key == pg.K_g:
                        if self.ship.base_ammo > 0:
                            self.sounds[2].play()
                            if self.ship.gun == "missile":
                                self.ship.gun = "beam"
                            else:
                                self.ship.gun = "missile"

                    if event.key == pg.K_c:
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

                    if event.key == pg.K_r and self.game_over:
                        self.reset(screen_size)

                    if event.key == pg.K_F2:
                        self.debug()

                    if event.key == pg.K_ESCAPE:
                        self.pause = not self.pause

                    if event.key == pg.K_q and (event.mod & pg.KMOD_CTRL):
                        running = False

                    if event.key == pg.K_m:
                        self.play_sound = not self.play_sound
                        if not self.play_sound:
                            pg.mixer.music.stop()
                        else:
                            pg.mixer.music.play(-1)

                elif event.type == pg.MOUSEBUTTONDOWN:
                    for skill in self.skills.skills:
                        if skill.is_hovered(pg.mouse.get_pos()):
                            self.skills.unlock_or_upgrade(skill, self.ship)

                elif event.type == JOYBUTTONDOWN:
                    if event.button == 0:
                        new_projectiles = self.ship.shoot(self.base, self.last_shot_time, self.ship.shot_cooldown,
                                                          self.play_sound, self.sounds)
                        self.projectiles.add(new_projectiles)
                        self.last_shot_time = pg.time.get_ticks()
                    if event.button == 1:
                        self.skill_tab.active = not self.skill_tab.active
                        self.stats_tab.active = not self.stats_tab.active

                    if event.button == 2:
                        if self.ship.base_ammo > 0:
                            self.sounds[2].play()
                            if self.ship.gun == "missile":
                                self.ship.gun = "beam"
                            else:
                                self.ship.gun = "missile"

                    if event.button == 3 and self.game_over:
                        self.reset(screen_size)

                    if controller.get_button(4) and controller.get_button(5):
                        if not self.charge_active and self.ship.charges > 0:
                            self.charge_active = True
                            self.charge_start_time = pg.time.get_ticks()

                    if event.button == 6:
                        if self.pause:
                            running = False

                    if event.button == 7:
                        self.pause = not self.pause

                elif event.type == JOYBUTTONUP:
                    if event.button in (4, 5) and self.charge_active:
                        self.ship.super_charge(joysticks, self.score,self.explosions,
                                               self.asteroids, self.frame_explode, self.frame_big_explode)
                        self.screen_shake = 50
                        self.charge_active = False
                        self.sounds[1].play()
                        if joysticks:
                            controller.stop_rumble()

                elif event.type == JOYAXISMOTION:
                    if not self.pause:
                        while len(self.joy_axis) <= event.axis:
                            self.joy_axis.append(0.0)
                        self.joy_axis[event.axis] = event.value if abs(event.value) > self.deadzone else 0.0

            if not running:
                break

            if self.charge_active:
                if joysticks:
                    controller.rumble(self.charge_rumble, 1,50)
                charge_elapsed = pg.time.get_ticks() - self.charge_start_time
                charge_ratio = min(1.0, charge_elapsed / self.charge_duration)

            screen.fill((0, 0, 0))
            dt = clock.tick(self.fps) / 1000

            self.update_movement(dt, screen_size)

            mouse_pos = pg.mouse.get_pos()
            self.hide_cursor(mouse_pos)

            if pg.time.get_ticks() - self.last_move_time > self.cursor_hide_delay:
                self.cursor_visible = False

            if not self.pause and not self.game_over:
                self.update_game(dt, screen_size, hud_padding)
                self.update_time()

            if self.tutorial_on:
                self.tutorial.update(self, dt)

            self.render(screen, font)

            if not self.game_over:
                self.update_hud(font, screen, hud_ratio)

            if self.cursor_visible:
                screen.blit(self.cursor_sprite, mouse_pos)

            if self.game_over:
                self.game_lost(font, screen, screen_size)

            if self.screen_shake > 0:
                self.screen_shake -= 1

            render = [0,0]
            if self.screen_shake:
                render = self.ship.taken_damage()
                if joysticks:
                    controller.rumble(0.5, 1, 20)
            if not self.game_over:
                screen.blit(pg.transform.scale(screen, screen_size), render)

            alpha = fade.update()
            if alpha > 0:
                fade_surface = pg.Surface(screen_size)
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))

            crt.render(screen)
        pg.quit()

    def update_movement(self, delta, screen_size):
        key_pressed = pg.key.get_pressed()
        joy_x = self.joy_axis[0]

        movement_x = 0
        movement_y = 0

        if key_pressed[K_LEFT]:
            movement_x -= self.ship.velocity * delta * 60
        if key_pressed[K_RIGHT]:
            movement_x += self.ship.velocity * delta * 60

        if key_pressed[K_UP]:
            movement_y -= self.ship.velocity * delta * 60
        if key_pressed[K_DOWN]:
            movement_y += self.ship.velocity * delta * 60

        movement_x += joy_x * self.ship.velocity * delta * 60
        movement_y += self.joy_axis[1] * self.ship.velocity * delta * 60

        self.ship_x = max(0, min(screen_size[0] - self.base.get_width(),
                                 self.ship_x + movement_x))
        self.ship_y = max(0, min(screen_size[1] - self.base.get_height(),
                                 self.ship_y + movement_y))

        if movement_x < 0:
            self.ship.direction = "left"
        elif movement_x > 0:
            self.ship.direction = "right"
        else:
            self.ship.direction = "idle"
        self.ship.moving = movement_x != 0 or movement_y != 0

        if self.ship.moving:
            if self.ship.tower_boost_applied:
                self.ship.shield -= self.ship.tower_boost
                self.ship.tower_boost = 0
                self.ship.tower_boost_applied = False
        elif not self.ship.moving:
            if not self.ship.moving:
                for skill in self.skills.skills:
                    if skill.name == "Tower" and skill.unlocked:
                        skill.ability.apply(self.ship, skill.level)

        if key_pressed[K_SPACE]:
            current_time = pg.time.get_ticks()
            if current_time - self.last_shot_time >= self.ship.shot_cooldown:
                new_projectiles = self.ship.shoot(self.base, self.last_shot_time, self.ship.shot_cooldown,
                                                  self.play_sound, self.sounds)
                self.projectiles.add(new_projectiles)
                self.last_shot_time = current_time

    def render(self, screen, font):
        for i in self.stars:
            pg.draw.circle(screen, (255, 255, 255), (int(i[0]), int(i[1])),i[2])

        self.celestials.draw(screen)
        self.asteroids.draw(screen)
        self.projectiles.draw(screen)
        self.upgrades.draw(screen)
        self.floating_numbers.draw(screen)
        for particle in self.particles:
            particle.draw(screen)

        img = self.base.copy()
        if self.ship.moving:
            overlay_index = self.anim_frame_overlay % len(self.frames_flying)
            overlay_frame = self.frames_flying[overlay_index]
            img.blit(overlay_frame, (0, 0))

        if self.debugging:
            for i in self.asteroids:
                pg.draw.rect(screen, (255, 0, 0), i.hitbox, 2)

            for u in self.upgrades:
                pg.draw.rect(screen, (0, 255, 0), u.rect, 2)

        if self.ship_alive:
            self.ship.rect.topleft = (self.ship_x, self.ship_y)
            screen.blit(img, self.ship.rect)
            if self.debugging:
                pg.draw.rect(screen, (255, 0, 0), self.ship.hitbox, 2)

        self.explosions.draw(screen)

        if self.skill_tab.active:
            mouse_pos = pg.mouse.get_pos()
            for skill in self.skills.skills:
                skill.is_hovered(mouse_pos)

        self.stats_tab.render(screen, font)
        self.skill_tab.render(screen, font)

        if self.tutorial_on:
            self.tutorial.render(screen, font, )

    def render_skills_tab(self, screen, rect, game_font):
        perk_points = game_font.render(f"Perks: {self.ship.perk_points}", True,(255, 255, 255))
        screen.blit(perk_points, (rect.x + 40, rect.y + 40))

        for skill in self.skills.skills:
            x, y = skill.pos
            frame = pg.transform.scale(skill.current_frame(), (64, 64))
            skill.rect.topleft = (rect.x + x, rect.y + y)
            screen.blit(frame, skill.rect)
            screen.blit(skill.icon_image, skill.rect)

    def render_stats_tab(self, screen, rect, game_font):
        stats = [
            f"Hitpoints: {int(self.ship.hitpoints)}/{int(self.ship.max_hitpoints)}",
            f"Shield: {int(self.ship.shield)}/{int(self.ship.max_shield)}",
            f"Ammo: {int(self.ship.ammo)}/{int(self.ship.base_ammo)}",
            f"Level: {int(self.ship.level)}",
            f"XP: {int(self.ship.xp)}/{int(self.ship.xp_to_next_level)}",
            f"Crit Chance: {int(self.ship.crit_chance * 100)}%",
            f"Crit Multiplier: {int(self.ship.crit_multiplier)}",
        ]
        y_offset = 40
        for stat in stats:
            text_surface = game_font.render(stat, True, (255, 255, 255))
            screen.blit(text_surface, (rect.x + 40, rect.y + y_offset))
            y_offset += 50

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

    def update_hud(self, font, screen, hud_ratio):
        self.stopwatch = font.render(
            f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}",
            True, "WHITE")
        screen.blit(self.stopwatch,
                    [hud_ratio['left'] + hud_ratio['width'] // 2 -
                     self.stopwatch.get_width() // 2, hud_ratio['top']])

        score_text = f"{self.score:05}"
        high_score = f"{self.high_score:05}"
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
        x_pos = hud_ratio['right'] - max(s.get_width()
                                         for s in high_score_surfaces + [
                                             high_score_surface])
        for line_surf in high_score_surfaces:
            screen.blit(line_surf, [x_pos, y_pos])
            y_pos += line_surf.get_height() + 2
        screen.blit(high_score_surface, [x_pos, y_pos])

        total_frames = len(self.hitpoints.frames) - 1
        if self.ship.hitpoints <= 0:
            hitpoints_frame = total_frames
        else:
            hitpoints_frame = (total_frames - (self.ship.hitpoints * total_frames)
                        // self.ship.max_hitpoints)
            hitpoints_frame = max(0, min(hitpoints_frame, total_frames))
        self.hitpoints.update(self.ship, hud_ratio, ['right', 'bottom'], hitpoints_frame, screen)

        shield_total_frames = len(self.shield.frames) - 1
        shield_frame = (shield_total_frames - (self.ship.shield * shield_total_frames)
                        // self.ship.max_shield)
        shield_frame = max(0, min(shield_total_frames, shield_frame))
        self.shield.update(self.ship, hud_ratio, ['right', 'bottom'], shield_frame, screen)

        experience_total_frames = len(self.xp.frames) - 1
        xp_frame = (experience_total_frames - (experience_total_frames * self.ship.xp)
                    // self.ship.xp_to_next_level)
        self.xp.update(self.ship, hud_ratio, ['right', 'bottom'], xp_frame, screen)

        ammo_total_frames = len(self.ammo.frames) - 1
        ammo_frame = (shield_total_frames - (self.ship.ammo * ammo_total_frames)
                    // self.ship.base_ammo)
        ammo_frame = max(0, min(ammo_total_frames, ammo_frame))
        self.ammo.update(self.ship, hud_ratio, ['right', 'bottom'], ammo_frame, screen)

    def update_game(self, delta, screen_size, hud_padding):
        self.ship.hit = False
        for i in self.stars:
            if not self.pause:
                i[1] += 2
            if i[1] > screen_size[1]:
                i[1] = 0
                i[0] = random.randint(0, screen_size[0])

        if not self.tutorial_on:
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

            if current_time - self.last_upgrade_spawn > self.upgrade_spawn_interval:
                self.last_upgrade_spawn = current_time

                for _ in range(random.randint(1, 2)):
                    x = random.randint(0, screen_size[0])
                    y = random.randint(-200, -50)

                    self.last_upgrade = upgd.get_upgrade()
                    upgrade = f"assets/{self.last_upgrade}.png"
                    new_upgrade = Upgrade(upgrade, x, y)
                    self.upgrades.add(new_upgrade)  # type: ignore

            current_time = pg.time.get_ticks()
            if current_time - self.last_asteroid_spawn > self.asteroid_spawn_interval:
                self.last_asteroid_spawn = current_time
                for _ in range(random.randint(1, self.asteroid_spawn_count)):
                    for _ in range(10):
                        new_asteroid = Asteroid(screen_size[0], min_y=-200,
                                                max_y=-50)
                        too_close = any(
                            abs(new_asteroid.rect.y - m.rect.y) < 60 for m in
                            self.asteroids)
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
                    if self.anim_index_left < len(frames) - 1:
                        self.anim_index_left += 1
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
        self.skill_tab.update()
        self.stats_tab.update()
        self.floating_numbers.update(delta)

        for particle in self.particles[:]:
            particle.update()
            if particle.timer <= 0:
                self.particles.remove(particle)

        if not self.direction_set:
            self.ship.direction = "idle"

        if self.ship_alive:
            self.ship.update_position(self.ship_x, self.ship_y)

        self.check_collision()
        current_time = pg.time.get_ticks()
        if self.active_upgrade == "power_up":
            self.ship.damage = self.ship.base_damage * self.ship.damage_multiplier * 2
            if current_time - self.upgrade_start_time >= self.upgrade_duration:
                self.active_upgrade = None
                self.ship.damage = self.ship.base_damage

        self.survival_bonus += 1
        if self.survival_bonus >= 60:
            self.survival_bonus = 0
            self.score += 1 * self.score_multiplier

    def level_enemies(self):
        for asteroid in self.asteroids:
            asteroid.hitpoints += 10 * self.ship.level
            asteroid.speed += 1

    def check_collision(self):
        asteroid_hit = pg.sprite.spritecollideany(self.ship, self.asteroids,# type: ignore
                                                  collided=lambda s,m: s.hitbox.colliderect(m.hitbox))
        if asteroid_hit:
            if random.random() <= self.ship.evasion:
                x, y = asteroid_hit.rect.center
                self.floating_numbers.add(FloatingNumber(x, y,"MISS", color=(255, 255, 100))) # type: ignore
                return

            self.ship.hit = True
            if self.ship.damage_multiplier > 1.0:
                x, y = self.ship.rect.centerx, self.ship.rect.top
                self.floating_numbers.add(FloatingNumber(x, y, "MULT LOSS",color=(255, 0, 0)))  # type: ignore
                self.ship.damage_multiplier = 1.0

            ship_center_x = self.ship.rect.centerx
            ship_center_y = self.ship.rect.centery
            explosion = Explosion(ship_center_x, ship_center_y,
                                  self.frame_explode)
            self.explosions.add(explosion)  # type: ignore

            for _ in range(10):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                self.particles.append(Particle((ship_center_x, ship_center_y),vel))

            asteroid_hit.kill()
            if self.play_sound:
                self.sounds[1].play()

            damage_per_frame = 0
            if self.ship.shield > 0:
                damage_per_frame = (max(1, self.ship.max_shield // 33) * self.ship.level)
                self.ship.shield -= damage_per_frame
            else:
                damage_per_frame = max(1, self.ship.max_hitpoints // 28) * self.ship.level
                self.ship.hitpoints -= damage_per_frame

            if hasattr(self.ship, "fortified_percent"):
                if self.ship.fortified_percent > 0:
                    shield_gain = int(damage_per_frame * self.ship.fortified_percent)
                    if hasattr(self.ship, "fortified_cap"):
                        shield_gain = min(shield_gain, self.ship.fortified_cap)
                    self.ship.shield += shield_gain

            self.screen_shake = 20

            if self.ship.hitpoints <= 0:
                self.game_over = True
                self.ship.kill()
                self.ship_alive = False
                pg.mixer.music.stop()
                self.game_over = True

        hits = pg.sprite.groupcollide(self.projectiles, self.asteroids,
                                      True, False)
        for asteroid in hits.values():
            current_time = pg.time.get_ticks()
            if current_time > self.ship.maniac_boost_end:
                self.ship.maniac_boost = 0

            effective_crit_chance = min(1.0, (self.ship.crit_chance/100) + self.ship.maniac_boost)
            if random.random() < effective_crit_chance:
                damage_per_frame = self.ship.damage * self.ship.crit_multiplier
                color = (255, 50, 50)
                size = 36
            else:
                damage_per_frame = self.ship.damage
                color = (255, 200, 0)
                size = 24

            if not self.ship.hit:
                self.ship.damage_multiplier += 0.1
            damage_per_frame *= self.ship.damage_multiplier

            if self.ship.hit:
                self.ship.damage_multiplier = 1.0

            asteroid[0].hitpoints -= damage_per_frame
            x, y = asteroid[0].rect.center

            if not self.ship.hit:
                mult_x, mult_y = self.ship.rect.centerx, self.ship.rect.top
                self.add_multiplier(mult_x, mult_y, f"x{self.ship.damage_multiplier:.2f}",
                                    color=color, font_size=size)

            self.floating_numbers.add(FloatingNumber(x, y, int(damage_per_frame), color=color, font_size=size))  # type: ignore
            impact = ImpactFrame(asteroid[0].rect.centerx,asteroid[0].rect.centery,
                                 self.frame_explode[0])
            self.explosions.add(impact) # type: ignore
            for _ in range(10):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                self.particles.append(Particle((asteroid[0].rect.centerx, asteroid[0].rect.centery),vel))
            if asteroid[0].hitpoints <= 0:
                asteroid[0].kill()
                if maniac_skill := next((s for s in self.skills.get_unlocked()
                                         if s.name == "Maniac"), None):
                    maniac_skill.ability.apply(self.ship, maniac_skill.level)
                explosion = Explosion(asteroid[0].rect.centerx,
                                      asteroid[0].rect.centery,
                                      self.frame_explode)
                self.explosions.add(explosion)  # type: ignore
                if self.play_sound:
                    self.sounds[1].play()
                self.score += self.ship.level * 10 * self.score_multiplier
                self.ship.gain_xp(self.formulize(self.ship.level), self.sounds)

        upgrade_hit = pg.sprite.spritecollide(self.ship, self.upgrades, False,# type: ignore
                                              collided=lambda s,u: s.hitbox.colliderect(u.rect))
        if upgrade_hit:
            for upgrade in upgrade_hit:
                upgrade.kill()
                if self.play_sound:
                    self.sounds[2].play()
                if self.last_upgrade == "power_up":
                    self.active_upgrade = "power_up"
                    self.upgrade_start_time = pg.time.get_ticks()
                elif self.last_upgrade == "shield":
                    self.ship.shield = min(self.ship.shield + 10,
                                           self.ship.max_shield)

    def add_multiplier(self, x, y, text, color=(255, 255, 0),font_size=24):
        offset = 0
        for fn in self.floating_numbers:
            if abs(fn.rect.centerx - x) < 50 and abs(fn.rect.centery - y - offset) < 5:
                offset -= 30
        self.floating_numbers.add(
            FloatingNumber(x, y + offset, text, color=color, font_size=font_size) # type: ignore
        )

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
                self.asteroid_spawn_interval = max(100,self.asteroid_spawn_interval - 10)
                self.asteroid_spawn_count = min(32, self.asteroid_spawn_count + 1)
            if self.seconds >= 60:
                self.level_enemies()
                self.seconds = 0
                self.minutes += 1
                if self.minutes >= 60:
                    self.minutes = 0
                    self.hours += 1

    def formulize(self, level, base_xp=5):
        score_factor = self.score ** 0.5
        return int(base_xp * (level ** 1.2) + score_factor)

    def hide_cursor(self, mouse_pos):
        if mouse_pos != self.last_cursor_pos:
            self.last_cursor_pos = mouse_pos
            self.last_move_time = pg.time.get_ticks()
            self.cursor_visible = True

    def reset(self, screen_size):
        saved_stats = self.ship.get_stats()

        self.projectiles.empty()
        self.asteroids.empty()
        self.explosions.empty()
        self.upgrades.empty()
        self.floating_numbers.empty()
        self.particles.clear()

        framew = self.sprite_sheet.sheet.get_width() // self.cols
        frameh = self.sprite_sheet.sheet.get_height()
        self.ship.rect.topleft = (screen_size[0] // 2 - framew // 2 - 25,
                                  screen_size[1] // 2 + 200)
        self.ship.hitbox.center = self.ship.rect.center

        for attr, value in saved_stats.items():
            setattr(self.ship, attr, value)

        self.ship_alive = True
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

    def game_lost(self, font, screen, screen_size):
        now = pg.time.get_ticks()
        if now - self.last_blink > 500:
            self.count += 1
            self.last_blink = now

        colors = ["RED", (0, 0, 0, 0)]
        game_over = font.render("GAME OVER", True, colors[self.count % 2])

        if self.play_sound:
            self.sounds[-1].play()
            self.game_over_fx = False

        if self.score > self.high_score:
            self.high_score = self.score

        score_text = font.render(f"{self.score:05}", True, "WHITE")
        stopwatch = self.stopwatch
        game_over_x = self.center(game_over, screen_size)
        game_over_y = screen_size[1] // 2
        screen.blit(game_over, [game_over_x, game_over_y])
        screen.blit(score_text, [self.center(score_text, screen_size),  game_over_y + 25])
        screen.blit(stopwatch, [self.center(stopwatch, screen_size), game_over_y + 50])

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