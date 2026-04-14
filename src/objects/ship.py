from ursina import *

class Ship:
    def __init__(self):
        self.entity = Entity()
        self.velocity = Vec3(0, 0, 0)
        self.thrust_power = 10

    def update(self):
        self._handle_input()
        self.entity.position += self.velocity * time.dt

    def _handle_input(self):
        thrust = Vec3(0, 0, 0)

        if held_keys['w']:
            thrust += self.entity.forward
        if held_keys['s']:
            thrust -= self.entity.forward
        if held_keys['a']:
            thrust -= self.entity.right
        if held_keys['d']:
            thrust += self.entity.right
        if held_keys['space']:
            thrust += Vec3(0, 1, 0)
        if held_keys['shift']:
            thrust -= Vec3(0, 1, 0)

        self.velocity += thrust * self.thrust_power * time.dt
        self.velocity *= 0.98