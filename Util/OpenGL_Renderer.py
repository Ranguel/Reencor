import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


def set_mode_opengl(size):
    pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    glViewport(0, 0, size[0], size[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, (size[0] / size[1]), 0.1, 1000.0)
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
    glLightfv(GL_LIGHT0, GL_POSITION, [-1, 1, 2, 0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.9, 0.9, 0.9, 1])
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
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data
    )
    return texture_id, (width, height)


def font_texture(font, text, color=(128, 128, 128)):
    texture_data = font.render(text, True, color)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    img_data = pygame.image.tostring(texture_data, "RGBA", True)
    width, height = texture_data.get_size()
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data
    )
    return texture_id, (width, height)


def draw_texture(
    texture_id,
    pos: list = (0, 0, 0),
    size: list = (0, 0),
    flip: list = (False, False),
    tint: list = (255, 255, 255, 255),
    angle: list = (0, 0, 0),
    repeat: bool = False,
    glow: float = 0,
    always_on_top: bool = False,
    center_origin: bool = False,
):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    x, y, z = list(pos) + [0] if len(pos) == 2 else pos
    if always_on_top:
        glDisable(GL_DEPTH_TEST)
    wrap_mode = GL_REPEAT if repeat else GL_CLAMP_TO_EDGE
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap_mode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap_mode)
    tex_scale_x = size[0] / 100 if repeat else 1
    tex_scale_y = size[1] / 100 if repeat else 1
    u1, u2 = (tex_scale_x, 0) if flip[0] else (0, tex_scale_x)
    v1, v2 = (0, tex_scale_y) if flip[1] else (tex_scale_y, 0)
    glPushMatrix()

    if center_origin:
        glTranslatef(x, y, z)
        glRotatef(angle[0], 1, 0, 0)
        glRotatef(angle[1], 0, 1, 0)
        glRotatef(angle[2], 0, 0, 1)
        glTranslatef(-size[0] / 2, -size[1] / 2, 0)
    else:
        glTranslatef(x + size[0] / 2, y + size[1] / 2, z)
        glRotatef(angle[0], 1, 0, 0)
        glRotatef(angle[1], 0, 1, 0)
        glRotatef(angle[2], 0, 0, 1)
        glTranslatef(-size[0] / 2, -size[1] / 2, 0)

    glow_color = [tint[0] / 255 * glow, tint[1] / 255 * glow, tint[2] / 255 * glow, 1.0]
    glMaterialfv(GL_FRONT, GL_EMISSION, glow_color)
    glColor4f(tint[0] / 255, tint[1] / 255, tint[2] / 255, tint[3] / 255)
    glBegin(GL_QUADS)
    glTexCoord2f(u1, v1)
    glVertex3f(0, size[1], 0)
    glTexCoord2f(u2, v1)
    glVertex3f(size[0], size[1], 0)
    glTexCoord2f(u2, v2)
    glVertex3f(size[0], 0, 0)
    glTexCoord2f(u1, v2)
    glVertex3f(0, 0, 0)
    glEnd()
    glMaterialfv(GL_FRONT, GL_EMISSION, [0, 0, 0, 1])
    glPopMatrix()
    if always_on_top:
        glEnable(GL_DEPTH_TEST)


def draw_cross(pos=(0, 0, 0), size=40, color=(255, 255, 255, 255), thickness=2):
    x, y, z = pos + [0] if len(pos) == 2 else pos
    half_size = size / 2
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glColor4f(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)
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


def draw_line(
    pos=(0, 0, 0), end_pos=(1, 1, 1), color=(255, 255, 255, 255), thickness=2
):
    x, y, z = pos + [0] if len(pos) == 2 else pos
    ex, ey, ez = end_pos + [0] if len(end_pos) == 2 else end_pos
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glColor4f(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)
    glLineWidth(thickness)
    glBegin(GL_LINES)
    glVertex3f(x, y, z)
    glVertex3f(ex, ey, ez)
    glEnd()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)

def draw_rect(
    rect, color=(255, 255, 255, 255), thickness=0, z_offset=0, glow=1
):
    x, y, width, height = rect
    glPushMatrix()
    glTranslatef(0, 0, z_offset)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glUseProgram(0)
    glColor4f(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)
    glow_color = [
        color[0] / 255 * glow,
        color[1] / 255 * glow,
        color[2] / 255 * glow,
        1.0,
    ]
    glMaterialfv(GL_FRONT, GL_EMISSION, glow_color)
    if not thickness:
        glBegin(GL_QUADS)
    else:
        glLineWidth(thickness)
        glBegin(GL_LINE_LOOP)

    glVertex3f(x, y + abs(height), 0)
    glVertex3f(x + abs(width), y + abs(height), 0)
    glVertex3f(x + abs(width), y, 0)
    glVertex3f(x, y, 0)

    glEnd()
    if thickness:
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


def palette_swap(image, palette):
    new = pygame.PixelArray(image)
    for color in palette:
        new.replace(tuple(color[0]), tuple(color[1]), 0.01)
    del new
    return image


class Camera:
    def __init__(self, smoothness: float = 0.2):
        self.smoothness = smoothness
        self.draw_shake = [0, 0, 0, 0, 0, 0]
        self.pos = [0, 0, -400]
        self.target_x, self.target_y, self.target_z = 0, 0, 0

    def update(self, pos, *args):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.target_x, self.target_y, self.target_z = pos
        self.pos[0] += (
            self.target_x - self.pos[0]
        ) * self.smoothness + self.draw_shake[0]
        self.pos[1] += (
            self.target_y - self.pos[1]
        ) * self.smoothness + self.draw_shake[1]
        self.pos[2] += (self.target_z - self.pos[2]) * self.smoothness
        gluLookAt(
            self.pos[0],
            self.pos[1],
            self.pos[2],
            self.pos[0],
            self.pos[1],
            self.pos[2] - 100,
            0,
            1,
            0,
        )


class Screen:
    def __init__(self, size: list = (800, 600)):
        self.size, self.draw_list = size, []

    def draw_texture(
        self,
        texture_id: int,
        pos: list = [0, 0, 0],
        size: list = [0, 0],
        flip: list = [False, False],
        tint: list = (255, 255, 255, 255),
        angle: list = [0, 0, 0],
        repeat: bool = False,
        glow: float = 0,
        always_on_top: bool = False,
        center_origin: bool = False,
    ):
        self.draw_list.append(
            (
                draw_texture,
                texture_id,
                pos,
                size,
                flip,
                tint,
                angle,
                repeat,
                glow,
                always_on_top,
                center_origin,
            )
        )

    def draw_rect(
        self,
        rect: list = (1, 1, 1, 1),
        color: list = (255, 255, 255, 255),
        border_thickness: int = 1,
        z_offset: int = 0,
        glow: float = 1,
    ):
        self.draw_list.append(
            (draw_rect, rect, color, border_thickness, z_offset, glow)
        )

    def draw_cross(
        self, pos: list = (0, 0), size: int = 20, color: list = (255, 255, 255, 255)
    ):
        self.draw_list.append((draw_cross, pos, size, color))

    def draw_teapod(
        self, pos: list = (0, 0, 0), scale: list = (0, 0, 0), color: list = (0, 0, 0, 0)
    ):
        self.draw_list.append((draw_teapod, pos, scale, color))

    def draw_line(
        self,
        pos: list = (0, 0, 0),
        end_pos: list = (1, 1, 1),
        color: list = (255, 255, 255, 255),
        thickness: int = 2,
    ):
        self.draw_list.append((draw_line, pos, end_pos, color, thickness))

    def display(self, tone: list = (255, 255, 255, 255)):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for draw_calls in self.draw_list:
            draw_calls[0](*draw_calls[1:])
        self.draw_list.clear()


def get_string_size(image_dict: dict, string: str = "", scale: tuple = (1, 1)):
    total_width = 0
    max_height = 0
    for i in string:
        total_width += image_dict["font " + i][1][0] * scale[0]
        max_height = (
            image_dict["font " + i][1][1] * scale[1]
            if image_dict["font " + i][1][1] * scale[1] > max_height
            else max_height
        )
    return total_width, max_height


def get_texture_string_size(
    image_dict: dict,
    texture_list: list = [],
    scale: tuple = (1, 1),
):
    texture_list = [
        texture for texture in texture_list if texture.get("image", "") in image_dict
    ]
    total_width = 0
    max_height = 0
    for texture in texture_list:
        char_width, char_height = (
            texture["size"] if texture.get("size") else image_dict[texture["image"]][1]
        )
        total_width += char_width * scale[0]
        max_height = max(max_height, char_height * scale[1])

    return (total_width, max_height)


def draw_string(
    image_dict: dict,
    screen: object = Screen,
    string: str = "",
    pos: list = [0, 0, 0],
    scale: tuple = (1, 1),
    color: tuple = (255, 255, 255, 255),
    alignment: str = "right",
    top: bool = True,
):
    offset_turn = 0
    for i in string:
        screen.draw_texture(
            image_dict["font " + i][0],
            (
                pos[0]
                + offset_turn * scale[0]
                - (
                    0
                    if alignment == "right"
                    else sum([image_dict["font " + n][1][0] for n in string]) * scale[0]
                ),
                pos[1],
                pos[2],
            ),
            (
                image_dict["font " + i][1][0] * scale[0],
                image_dict["font " + i][1][1] * scale[1],
            ),
            (False, False),
            color,
            [0, 0, 0],
            False,
            1,
            top,
        )
        offset_turn += image_dict["font " + i][1][0]


def draw_texture_as_string(
    image_dict: dict,
    screen: object = Screen,
    texture_list: list = [],
    pos: list = [0, 0, 0],
    scale: tuple = (1, 1),
    color: tuple = (255, 255, 255, 255),
    alignment: str = "right",
    top: bool = True,
):
    offset_turn = 0
    texture_list = [
        texture for texture in texture_list if texture.get("image", "") in image_dict
    ]
    total_width = (
        sum(
            (
                texture["size"][0]
                if texture.get("size", False)
                else image_dict[texture["image"]][1][0]
            )
            for texture in texture_list
        )
        * scale[0]
    )

    for texture in texture_list:
        char_width, char_height = (
            texture["size"]
            if texture.get("size", False)
            else image_dict[texture["image"]][1]
        )
        draw_x = pos[0] + offset_turn * scale[0]
        if alignment != "right":
            draw_x -= total_width

        screen.draw_texture(
            image_dict[texture["image"]][0],
            (draw_x, pos[1], pos[2]),
            ((char_width * scale[0], char_height * scale[1])),
            (False, False),
            color,
            [0, 0, 0],
            False,
            1,
            top,
        )
        offset_turn += char_width
