class Shockwave:
    def __init__(self, center, max_radius=700, speed=25):
        self.x, self.y = center
        self.radius = 0
        self.max_radius = max_radius
        self.speed = speed
        self.alive = True

    def update(self, dt=1.0):
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.alive = False

    def affects(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx * dx + dy * dy <= self.radius * self.radius