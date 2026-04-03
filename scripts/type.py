import pygame

class Typewriter:
    def __init__(self, pos, message, screen, font, speed=50,
                 color=(255, 255, 255)):
        self.pos = pos
        self.message = message
        self.screen = screen
        self.font = font
        self.color = color
        self.speed = speed
        self.start_time = pygame.time.get_ticks()
        self.done = False
        self.current_index = 0

    def update(self):
        if not self.done:
            elapsed = pygame.time.get_ticks() - self.start_time
            self.current_index = min(len(self.message), elapsed // self.speed)
            if self.current_index == len(self.message):
                self.done = True

    def draw(self):
        text_to_render = self.message[:self.current_index]
        if text_to_render:
            snip = self.font.render(text_to_render, True, self.color)
            self.screen.blit(snip, self.pos)