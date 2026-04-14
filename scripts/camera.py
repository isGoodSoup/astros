import math

class Camera:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h

        self.fov = 400
        self.z_offset = 200

        self.x = 0
        self.y = 0
        self.z = 0

        self.yaw = 0
        self.pitch = 0

    def project(self, x, y, z):
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z

        cos_y = math.cos(self.yaw)
        sin_y = math.sin(self.yaw)

        cx = dx * cos_y - dy * sin_y
        cy = dx * sin_y + dy * cos_y

        cos_p = math.cos(self.pitch)
        sin_p = math.sin(self.pitch)

        cz = dz * cos_p - cy * sin_p
        cy = dz * sin_p + cy * cos_p

        cz += self.z_offset

        if cz < 1:
            cz = 1

        scale = self.fov / cz

        sx = cx * scale + self.w // 2
        sy = cy * scale + self.h // 2

        return sx, sy, scale
