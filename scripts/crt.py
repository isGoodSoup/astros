import struct
import pygame, os, sys
import moderngl

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        absolute_path = os.path.join(sys._MEIPASS, relative)
    else:
        absolute_path = os.path.join(relative)
    return absolute_path

class CRT:
    def __init__(self, screen, style=1, virtual_resolution=(800, 600), cpu_only=False,
                 fullscreen=False):
        pygame.init()
        self.virtual_resolution = virtual_resolution
        self.cpu_only = cpu_only
        self.screen = screen
        self.fullscreen = fullscreen
        if not self.cpu_only:
            self.ctx = moderngl.create_context()
            self.texture_coordinates = [0, 1, 1, 1,
                                        0, 0, 1, 0]
            self.world_coordinates = [-1, -1, 1, -1,
                                      -1, 1, 1, 1]
            self.render_indices = [0, 1, 2,
                                   1, 2, 3]
            self.style = style
            self.prog = self.ctx.program(vertex_shader=open(resource_path('shaders/VERTEX_SHADER.glsl')).read(),
                fragment_shader=open(resource_path('shaders/FRAGMENT_SHADER.glsl')).read())
            self.prog['mode'] = self.style

            self.screen_texture = self.ctx.texture(self.virtual_resolution, 4,
                pygame.image.tostring(screen,"RGBA",False))
            self.screen_texture.repeat_x = False
            self.screen_texture.repeat_y = False

            self.vbo = self.ctx.buffer(
                struct.pack('8f', *self.world_coordinates))
            self.uvmap = self.ctx.buffer(
                struct.pack('8f', *self.texture_coordinates))
            self.ibo = self.ctx.buffer(struct.pack('6I', *self.render_indices))

            self.vao_content = [
                (self.vbo, '2f', 'vert'),
                (self.uvmap, '2f', 'in_text'),
            ]

            self.vao = self.ctx.vertex_array(self.prog, self.vao_content,
                                             index_buffer=self.ibo)
        else:
            self.display = pygame.display.get_surface()

    def change_shader(self):
        if not self.cpu_only:
            self.__init__(self.screen, (self.style + 1) % 3, self.virtual_resolution)

    def render(self, surface):
        if not self.cpu_only:
            texture_data = pygame.image.tostring(surface, "RGBA", False)
            self.screen_texture.write(texture_data)
            self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
            self.screen_texture.use()
            self.vao.render()
            pygame.display.flip()
        else:
            self.display.blit(self.screen, (0, 0))
            pygame.display.update()

    def fullscreen(self, real_resolution):
        if not self.cpu_only:
            if not self.fullscreen:
                pygame.display.set_mode(real_resolution, pygame.DOUBLEBUF | pygame.OPENGL)
            else:
                pygame.display.set_mode(real_resolution, pygame.DOUBLEBUF |
                                        pygame.OPENGL | pygame.FULLSCREEN)
        else:
            if not self.fullscreen:
                pygame.display.set_mode(self.virtual_resolution)
            else:
                pygame.display.set_mode(self.virtual_resolution, pygame.FULLSCREEN)

    def __call__(self, surface):
        return self.render(surface)