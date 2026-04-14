from ursina import Vec3, distance

class FloatingOrigin:
    def __init__(self, ship, world_root):
        self.ship = ship
        self.world_root = world_root
        self.recenter_threshold = 500
        self.total_offset = Vec3(0, 0, 0)

    def update(self):
        ship_pos = self.ship.entity.position

        if distance(ship_pos, Vec3(0, 0, 0)) > self.recenter_threshold:
            self._recenter_world()

    def _recenter_world(self):
        offset = self.ship.entity.position

        for entity in self.world_root.children:
            entity.world_position -= offset

        self.total_offset += offset
        self.ship.entity.position = Vec3(0, 0, 0)