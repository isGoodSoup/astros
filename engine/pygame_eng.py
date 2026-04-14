import pygame

class PygameEngine(Engine):
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True

    def poll_events(self):
        return pygame.event.get()

    def begin_frame(self):
        pass

    def end_frame(self):
        pygame.display.flip()
        self.clock.tick(60)

    def draw_text(self, text, pos, color):
        font = pygame.font.Font(None, 32)
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

    def clear(self):
        self.screen.fill((0, 0, 0))

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False