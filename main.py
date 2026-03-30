import pygame

from ship import Ship
from sprites import SpriteSheet


animation_steps = 4
animation_cooldown = 100

class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = (pygame.display.Info().current_w/4,
                            pygame.display.Info().current_h/1.5)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.SCALED, vsync=1)
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        self.frame = 0

        self.sprite_sheet = SpriteSheet("assets/ship.png")
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         self.sprite_sheet.sheet.get_width(),
                         self.sprite_sheet.sheet.get_height(), columns=4)
        self.ship_x, self.ship_y = (self.screen_size[0]/2 -
                                    self.ship.width/2, self.screen_size[1] - 200)

        self.cols = 8
        self.frames = []
        framew = self.sprite_sheet.sheet.get_width() // self.cols
        frameh = self.sprite_sheet.sheet.get_height()
        for i in range(animation_steps):
            img = self.sprite_sheet.get_image(i, framew, frameh, scale=2,
                                              columns=self.cols)
            self.frames.append(img)
        self.last_update = pygame.time.get_ticks()

    def run(self):
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill((0,0,0))

            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= animation_cooldown:
                self.last_update = current_time
                self.frame += 1
                if self.frame >= len(self.frames):
                    self.frame = 0
                self.ship.sprite = self.frames[self.frame]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.blit(self.ship.sprite, [self.ship_x, self.ship_y])
            key_pressed = pygame.key.get_pressed()
            if key_pressed[pygame.K_LEFT] and self.ship_x > 0:
                self.ship_x -= self.ship.velocity
            if key_pressed[pygame.K_RIGHT] and self.ship_x < self.screen_size[0] - self.ship.sprite.get_width():
                self.ship_x += self.ship.velocity
            if key_pressed[pygame.K_UP] and self.ship_y > 0:
                self.ship_y -= self.ship.velocity
            if key_pressed[pygame.K_DOWN] and self.ship_y < self.screen_size[1] - self.ship.sprite.get_height():
                self.ship_y += self.ship.velocity
            pygame.display.update()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()