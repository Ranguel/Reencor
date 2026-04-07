import numpy

from engine.id.entity import EntityIdGenerator
from engine.constant.physics import *
from engine.constant.ui import *
from engine.math.vector import rotate_vector_2d
from engine.effect.shake import ShakeComponent


class Label:
    def __init__(
        self,
        text: str = "none",
        font: str = "font",
        color: tuple = (1, 1, 1, 1),
        side: ScreenSide = ScreenSide.LEFT,
        indent: Textindent = Textindent.LEFT,
        max_lenght: int = 100,
        background: tuple = (0, 0, 0, 0),
        size: int = 0.1,
        parent: object = None,
        space: PositionSpace = PositionSpace.GLOBAL,
        position: numpy.array = numpy.array([0, 0], dtype=numpy.float32),
        rotation: numpy.float32 = numpy.float32(0),
        scale: numpy.array = numpy.array([1, 1], dtype=numpy.float32),
        show: bool = True,
        life_time: bool = False,
        function: callable = None,
        params: any = None,
        subtype: UISubtype = UISubtype.COMBO,
    ):
        self.id = EntityIdGenerator.next()
        self.type = UIType.LABEL
        self.subtype = subtype
        self.text = text
        self.font = font
        self.color = color
        self.side = side
        self.indent = indent
        self.max_lenght = max_lenght
        self.background = background
        self.size = size
        self.life_time = life_time if life_time else False

        self.dimension = 2
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.parent = parent
        self.space = space
        self.children = []

        self.function = function
        self.params = params

        self.draw = []
        self.render_interruption = True
        self.render_list = []
        self.draw_shake = ShakeComponent()
        self.show = show
        self.show_timer = 0

        self.paragraph = [
            "",
        ]

        self.string_update(self.text)

    def string_update(self, new_string: str):
        """Update the label's string and mark it for re-rendering."""

        if new_string != self.text:
            self.text = new_string
            self.render_interruption = True  # Mark for re-rendering

        self.paragraph = [
            "",
        ]

        text = self.text.split(" ")
        line_index = 0
        for word in text:
            if len(self.paragraph[line_index]) + len(word) > self.max_lenght:
                line_index += 1
                self.paragraph.append("")
            self.paragraph[line_index] += word + " "

    def color_update(self, new_color: tuple):
        """Update the label's color and mark it for re-rendering."""

        if new_color != self.color:
            self.color = new_color
            self.render_interruption = True  # Mark for re-rendering

    def size_update(self, new_size: int):
        """Update the label's size and mark it for re-rendering."""

        if new_size != self.size:
            self.size = new_size
            self.render_interruption = True  # Mark for re-rendering

    def position_update(self, new_position: numpy.array):
        """Update the label's position and mark it for re-rendering."""

        if not numpy.array_equal(new_position, self.position):
            self.position = new_position
            self.render_interruption = True  # Mark for re-rendering

    def _draw_shake_interruption(self):
        """Check if shake effect is active and mark for re-rendering if so."""

        if self.draw_shake.active:
            self.render_interruption = True

    def _show_timer_update(self):
        """Update show timer and visibility state."""

        if self.show_timer > 0:
            self.show_timer -= 1
            if self.show_timer <= 0:
                self.show = not self.show
                self.render_interruption = (
                    True  # Mark for re-rendering when visibility changes
                )

    def _life_time_update(self):
        """Update life timer and mark for deletion if expired."""

        if isinstance(self.life_time, int) and not isinstance(self.life_time, bool):
            self.life_time -= 1

    def update(self, **kwargs):
        self._draw_shake_interruption()
        self._show_timer_update()
        self._life_time_update()

    def paragraph_render(self, paragraph):
        for y_index, line in enumerate(paragraph):

            y_offset = -((y_index) * self.size)

            indent_offset = -(
                len(line) * 0.25
                if self.indent == Textindent.CENTER
                else len(line) * 0.5 if self.indent == Textindent.RIGHT else 0
            )

            for index, letter in enumerate(line):
                x_offset = (0.5 * index) * (
                    -1 if self.side == ScreenSide.RIGHT else 1
                ) + ((len(line) - 2) * 0.5 if self.side == ScreenSide.RIGHT else 0)

                position = self.position + rotate_vector_2d(
                    self.rotation,
                    ((indent_offset + x_offset) * self.size, y_offset),
                )

                texture = {
                    "color_texture": self.font + "/" + f"{ord(letter):04d}",
                    "position": position,
                }

                self.render_list.append(self._build_draw_command(texture))

            position = self.position + rotate_vector_2d(
                self.rotation,
                ((indent_offset) * self.size, y_offset),
            )
            size = ((len(line) - 1) * 0.5 * self.size, self.size)

            texture = {
                "tint": self.background,
                "position": position,
                "size": size,
                "chess": False,
                "program": "meter",
            }

            self.render_list.append(self._build_draw_command(texture))

    def render(self, **kwargs) -> list:
        """Compute draw commands for this UI element and push them into renderer.draw_queue."""

        if not self.show:
            return []  # Don't render if not visible

        if not self.render_interruption:
            return self.render_list

        self.render_list.clear()  # Clear previous render data
        self.render_interruption = False

        self.paragraph_render(self.paragraph)

        return self.render_list

    def _build_draw_command(self, texture: dict) -> dict:
        """Create a render dictionary for a single texture entry."""

        defaults = {
            "color_texture": "",
            "side": self.side == ScreenSide.RIGHT,
            "size": [self.size, self.size],
            "rotation": self.rotation,
            "tint": self.color,
            "program": "text",
        }

        draw_dict = defaults | texture

        color_texture = draw_dict["color_texture"]

        # compute shake & texture position
        shake_offset = self.draw_shake.update(0.16)[:2]
        position = draw_dict["position"] + rotate_vector_2d(self.rotation, shake_offset)

        # build final render dictionary
        return draw_dict | {
            "color_texture": color_texture,
            "position": position,
            "texture_aspect": color_texture,
        }
