from scripts.entity import Entity


class Alien(Entity):
    def __init__(self, color, x, y):
        super().__init__(f"assets/aliens/{color}.png", x, y, scale=False)