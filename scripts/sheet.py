import pygame

from scripts.utils import legacy


class SpriteSheet:
    def __init__(self, path):
        self.sheet = pygame.image.load(path).convert_alpha()

    @legacy
    def get_image(self, frame, width, height, scale=1, columns=16):
        sheet_width, sheet_height = self.sheet.get_size()

        cols = columns
        rows = sheet_height // height

        max_frame = (cols * rows) - 1
        frame = max(0, min(frame, max_frame))

        row = frame // cols
        col = frame % cols

        rect = pygame.Rect(
            col * width,
            row * height,
            width,
            height
        )

        image = self.sheet.subsurface(rect)
        return pygame.transform.scale(image, (width * scale, height * scale))

    def get_frame(self, index, cols, rows=1):
        sheet_width, sheet_height = self.sheet.get_size()

        frame_width = sheet_width // cols
        frame_height = sheet_height // rows

        max_index = cols * rows - 1
        index = max(0, min(index, max_index))

        col = index % cols
        row = index // cols

        rect = pygame.Rect(col * frame_width, row * frame_height,
            frame_width, frame_height)
        return self.sheet.subsurface(rect)