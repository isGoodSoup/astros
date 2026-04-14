from ursina import *

class CameraRig:
    def __init__(self, ship):
        self.ship = ship

        camera.parent = ship.entity
        camera.position = (0, 2, 0)
        camera.rotation = (0, 0, 0)

        mouse.locked = True
        self.sensitivity = 40

    def update(self):
        self._mouse_look()

    def _mouse_look(self):
        ship = self.ship.entity

        ship.rotation_y += mouse.velocity[0] * self.sensitivity
        camera.rotation_x -= mouse.velocity[1] * self.sensitivity
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)