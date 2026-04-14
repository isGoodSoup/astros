from ursina import Entity
from objects.ship import Ship
from objects.camera import CameraRig
from system.floaty import FloatingOrigin

class Game:
    def __init__(self):
        self.world_root = Entity()
        self.ship = Ship()
        self.camera_rig = CameraRig(self.ship)
        self.floating_origin = FloatingOrigin(self.ship, self.world_root)

    def update(self):
        self.ship.update()
        self.camera_rig.update()
        self.floating_origin.update()