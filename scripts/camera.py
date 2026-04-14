

class Camera:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h

        self.fov = 400
        self.z_offset = 200

        self.x = 0
        self.y = 0

    def project(self, x, y, z):
        z = z + self.z_offset
        if z <= 1:
            z = 1

        scale = self.fov / z
        x -= self.x
        y -= self.y
        sx = x * scale + self.w // 2
        sy = y * scale + self.h // 2
        return sx, sy, scale

    def project_scale(self, z):
        z = max(1, z + self.z_offset)
        return self.fov / z
