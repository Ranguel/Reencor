import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


def set_mode_opengl(size):
    pygame.display.set_mode(size, pygame.OPENGL |
                            pygame.DOUBLEBUF | pygame.RESIZABLE)
    glViewport(0, 0, size[0], size[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, (size[0]/size[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.1)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [-1, 1, -2, 0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [.9, .9, .9, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1])


def load_image_path(ruta):
    texture_data = pygame.image.load(ruta).convert_alpha()
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    img_data = pygame.image.tostring(texture_data, "RGBA", True)
    width, height = texture_data.get_size()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    return texture_id, (width, height)


def font_texture(font, text, color=(128, 128, 128)):
    texture_data = font.render(text, True, color)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    img_data = pygame.image.tostring(texture_data, "RGBA", True)
    width, height = texture_data.get_size()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    return texture_id, (width, height)


def draw_texture(texture_id, pos=(0, 0, 0), size=(0, 0), flip=(False, False), tint=(255, 255, 255, 255), angle=(0, 0, 0), repeat=False, glow=0, always_on_top=False):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    x, y, z = list(pos) + [0] if len(pos) == 2 else pos
    width, height = size
    if always_on_top:
        glDisable(GL_DEPTH_TEST)
    wrap_mode = GL_REPEAT if repeat else GL_CLAMP_TO_EDGE
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap_mode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap_mode)
    tex_scale_x = width / 100 if repeat else 1
    tex_scale_y = height / 100 if repeat else 1
    u1, u2 = (tex_scale_x, 0) if flip[0] else (0, tex_scale_x)
    v1, v2 = (0, tex_scale_y) if flip[1] else (tex_scale_y, 0)
    glPushMatrix()
    glTranslatef(x + width / 2, y + height / 2, z)
    glRotatef(angle[0], 1, 0, 0)
    glRotatef(angle[1], 0, 1, 0)
    glRotatef(angle[2], 0, 0, 1)
    glTranslatef(-width / 2, -height / 2, 0)
    glow_color = [tint[0] / 255 * glow, tint[1] / 255 * glow, tint[2] / 255 * glow, 1.0]
    glMaterialfv(GL_FRONT, GL_EMISSION, glow_color)
    glColor4f(tint[0]/255, tint[1]/255, tint[2]/255, tint[3]/255)
    glBegin(GL_QUADS)
    glTexCoord2f(u1, v1)
    glVertex2f(0, 0)
    glTexCoord2f(u2, v1)
    glVertex2f(width, 0)
    glTexCoord2f(u2, v2)
    glVertex2f(width, height)
    glTexCoord2f(u1, v2)
    glVertex2f(0, height)
    glEnd()
    glMaterialfv(GL_FRONT, GL_EMISSION, [0, 0, 0, 1])
    glPopMatrix()
    if always_on_top:
        glEnable(GL_DEPTH_TEST)


def draw_cross(pos=(0, 0, 0), size=40, color=(255, 255, 255, 255), thickness=2):
    x, y, z = pos+[0] if len(pos) == 2 else pos
    half_size = size / 2
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glColor4f(color[0]/255, color[1]/255, color[2]/255, color[3]/255)
    glLineWidth(thickness)
    glBegin(GL_LINES)
    glVertex3f(x - half_size, y, z)
    glVertex3f(x + half_size, y, z)
    glVertex3f(x, y - half_size, z)
    glVertex3f(x, y + half_size, z)
    glEnd()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)


def draw_line(pos=(0, 0, 0), end_pos=(1, 1, 1), color=(255, 255, 255, 255), thickness=2):
    x, y, z = pos + [0] if len(pos) == 2 else pos
    ex, ey, ez = end_pos + [0] if len(end_pos) == 2 else end_pos
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glColor4f(color[0]/255, color[1]/255, color[2]/255, color[3]/255)
    glLineWidth(thickness)
    glBegin(GL_LINES)
    glVertex3f(x, y, z)
    glVertex3f(ex, ey, ez)
    glEnd()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)


def draw_rect(rect, color=(255, 255, 255, 255), thickness=1, fill=False, z_offset=0, glow=1):
    x, y, width, height = rect
    glPushMatrix()
    glTranslatef(0, 0, z_offset)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glUseProgram(0)
    glColor4f(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)
    glow_color = [color[0] / 255 * glow, color[1] /
                  255 * glow, color[2] / 255 * glow, 1.0]
    glMaterialfv(GL_FRONT, GL_EMISSION, glow_color)
    if fill:
        glBegin(GL_QUADS)
    else:
        glLineWidth(thickness)
        glBegin(GL_LINE_LOOP)
    glVertex3f(x, y, 0)
    glVertex3f(x + width, y, 0)
    glVertex3f(x + width, y + height, 0)
    glVertex3f(x, y + height, 0)
    glEnd()
    if not fill:
        glLineWidth(1)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)


def draw_teapod(pos=(0, 0, 0), scale=(0, 0, 0), color=(0, 0, 0, 0)):
    glDisable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScalef(scale[0], scale[1], scale[2])
    glRotatef(pygame.time.get_ticks() * 0.05, 0, 1, 0)
    glColor4f(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)
    glutSolidTeapot(1)
    glPopMatrix()
    glEnable(GL_TEXTURE_2D)


class Camera:
    def __init__(self, smoothness=0.2):
        self.smoothness = smoothness
        self.draw_shake = [0, 0, 0, 0, 0, 0]
        self.pos = [0, 0, -400]
        self.target_x, self.target_y, self.target_z = 0, 0, 0

    def update(self, pos, *args):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.target_x, self.target_y, self.target_z = pos
        self.pos[0] += (self.target_x - self.pos[0]) * \
            self.smoothness + self.draw_shake[0]
        self.pos[1] += (self.target_y - self.pos[1]) * \
            self.smoothness + self.draw_shake[1]
        self.pos[2] += (self.target_z - self.pos[2]) * self.smoothness
        gluLookAt(self.pos[0], self.pos[1], self.pos[2],
                  self.pos[0], self.pos[1], self.pos[2]+100,
                  0, -1, 0)


class Screen:
    def __init__(
            self, size):
        self.size, self.draw_list = size, []

    def draw_texture(self, texture_id, pos=[0, 0, 0], size=[0, 0], flip=[False, False], tint=(255, 255, 255, 255), angle=[0, 0, 0], repeat=False, glow=0, always_on_top=False):
        self.draw_list.append(
            (draw_texture, texture_id, pos, size, flip, tint, angle, repeat, glow, always_on_top))

    def draw_rect(self, rect=(1, 1, 1, 1), color=(255, 255, 255, 255), border_thickness=1, fill=False, z_offset=0, glow=1):
        self.draw_list.append(
            (draw_rect, rect, color, border_thickness, fill, z_offset, glow))

    def draw_cross(self, pos=(0, 0), size=20, color=(255, 255, 255, 255)):
        self.draw_list.append((draw_cross, pos, size, color))

    def draw_teapod(self, pos=(0, 0, 0), scale=(0, 0, 0), color=(0, 0, 0, 0)):
        self.draw_list.append((draw_teapod, pos, scale, color))

    def draw_line(self, pos=(0, 0, 0), end_pos=(1, 1, 1), color=(255, 255, 255, 255), thickness=2):
        self.draw_list.append((draw_line, pos, end_pos, color, thickness))

    def display(self, tone=(255, 255, 255, 255)):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for draw_calls in self.draw_list:
            draw_calls[0](*draw_calls[1:])
        self.draw_list.clear()
