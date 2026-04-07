import pygame


class Window:
    def __init__(self, resolution, frame_rate=60, vsync=True):
        pygame.init()

        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )
        self.screen = pygame.display.set_mode(
            resolution, pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        )

        self.clock = pygame.time.Clock()
        self.resolution = resolution
        self.aspect_ratio = self.resolution[0] / self.resolution[1]
        self.aspect_ratio_inv = self.resolution[1] / self.resolution[0]

        self.vsync = vsync
        self.frame_rate = frame_rate

    def swap_buffers(self):
        pygame.display.flip()

    def tick(self):
        self.clock.tick(self.frame_rate)
