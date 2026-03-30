
class Ship:
    def __init__(self, sprite_sheet, x, y, frame, width, height, scale=3,
                 columns=1):
        self.sprite = sprite_sheet.get_image(frame, width, height, scale, columns)
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.velocity = 8
        self.state = "move"
        self.moving = False