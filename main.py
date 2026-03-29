import pygame

from ship import Ship
from sprites import SpriteSheet


animation_steps = 4
last_update = pygame.time.get_ticks()
animation_cooldown = 100

class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        self.frame = 0

        self.sprite_sheet = SpriteSheet("assets/ship.png")
        self.ship_x, self.ship_y = 0, 0
        self.ship = Ship(self.sprite_sheet, self.ship_x, self.ship_y,
                         self.frame, self.sprite_sheet.sheet.get_width(),
                         self.sprite_sheet.sheet.get_height(), columns=4)

        self.frames = []
        framew = self.sprite_sheet.sheet.get_width() // 4
        frameh = self.sprite_sheet.sheet.get_height()
        for i in range(animation_steps):
            img = self.sprite_sheet.get_image(i, framew, frameh, scale=3, columns=4)
            self.frames.append(img)

    def run(self):
        global last_update
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill((0,0,0))

            current_time = pygame.time.get_ticks()
            if current_time - last_update >= animation_cooldown:
                last_update = current_time
                self.frame += 1
                if self.frame >= len(self.frames):
                    self.frame = 0
                self.ship.sprite = self.frames[self.frame]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.screen.blit(self.ship.sprite, [self.screen_size[0]/2,
                                                self.screen_size[1]/2])
            pygame.display.update()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()