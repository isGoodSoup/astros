import pygame

class SpriteSheet:
    def __init__(self, path):
        self.sheet = pygame.image.load(path).convert_alpha()

    def get_image(self, frame, width, height, scale=1, columns=16):
        row = frame // columns
        col = frame % columns
        image = self.sheet.subsurface(pygame.Rect(col * width, row * height, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        return image