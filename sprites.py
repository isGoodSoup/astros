import pygame

class SpriteSheet:
    def __init__(self, path):
        self.sheet = pygame.image.load(path).convert_alpha()

    def get_image(self, frame, width, height, scale, columns, row=0):
        col = frame % columns
        img = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        img.blit(self.sheet, (0, 0), (col * width, row * height, width, height))
        img = pygame.transform.scale(img, (width * scale, height * scale))
        return img