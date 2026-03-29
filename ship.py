
class Ship:
    def __init__(self, x, y, sprite_sheet, frame, width, height, scale=3,
                 columns=1):
        self.sprite = sprite_sheet.get_image(frame, width, height, scale, columns)
        self.x, self.y = x, y