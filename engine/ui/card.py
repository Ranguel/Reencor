import numpy

from engine.id.entity import EntityIdGenerator
from engine.constant.physics import *
from engine.constant.ui import *
from engine.math.vector import rotate_vector_2d
from engine.effect.shake import ShakeComponent
from engine.action.state import build_state_buffer, find_next_state


class Card:
    def __init__(
        self,
        dict: dict = {},
        palette: int = 0,
        side: ScreenSide = ScreenSide.LEFT,
        state: str = "none",
        condition: set = set(),
        parent: object = None,
        space: PositionSpace = PositionSpace.GLOBAL,
        position: numpy.array = numpy.array([0, 0], dtype=numpy.float32),
        rotation: numpy.float32 = numpy.float32(0),
        scale: numpy.array = numpy.array([1, 1], dtype=numpy.float32),
        life_time: bool = False,
    ):
        self.id = EntityIdGenerator.next()
        self.dict = dict
        self.type = UIType.INDICATOR
        self.subtype = UISubtype.LIFE
        self.palette = palette
        self.side = side
        self.life_time = life_time if life_time else False

        self.dimension = 2
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.parent = parent
        self.space = space
        self.children = []

        self.draw = []
        self.render_interruption = True
        self.render_list = []
        self.draw_shake = ShakeComponent()

        self.state_current = state
        self.state_buffer = {}
        self.state_data = []
        self.frame_data = {}
        self.frame_interruption = True

        self.frame_total = 0
        self.frame_duration = 0
        self.frame_index = 1
        self.frame_counter = 1
        self.frame_repeat = 0

        self.condition = set(condition)
        self.command = set()
        self.input = set({"x_neutral", "y_neutral"})
        self.input_device = None
        self.input_interruption = False

        self.pending_changes = {}

        if state == "none":
            build_state_buffer(self, current_condition=self.input | self.condition)
            state_found = find_next_state(
                self, state_buffer=self.state_buffer, force=True
            )
        else:
            state_found = find_next_state(self, state_buffer={state: 2}, force=True)

    def _buffer_update(self):
        if self.input_interruption or (
            self.frame_index >= self.frame_total
            and self.frame_counter >= self.frame_duration
        ):
            build_state_buffer(
                self,
                current_condition=self.input | self.command | self.condition,
            )

    def _state_update(self):
        if (
            self.input_interruption
            or self.state_buffer
            or (
                self.frame_index >= self.frame_total
                and self.frame_counter >= self.frame_duration
            )
        ):
            find_next_state(self, self.state_buffer)

    def _counter_update(self):
        self.state_buffer = {
            timer: self.state_buffer[timer] - 1
            for timer in self.state_buffer
            if self.state_buffer[timer] > 0
        }

        self.frame_counter += 1

        if self.frame_interruption:
            self.frame_interruption = False

        if self.input_interruption:
            self.input_interruption = False

    def _frame_update(self):
        if (
            self.frame_counter >= self.frame_duration
            and self.frame_index < self.frame_total
        ) and self.state_current != "none":
            self.frame_interruption = True
            self.frame_data = self.state_data[self.frame_index]
            self.frame_index += 1

    def _life_time_update(self):
        """Update life timer and mark for deletion if expired."""

        if isinstance(self.life_time, int) and not isinstance(self.life_time, bool):
            self.life_time -= 1

    def update(self, **kwargs):
        self._buffer_update()
        self._state_update()
        self._counter_update()
        self._frame_update()
        self._life_time_update()

    def render(self, **kwargs) -> list:
        """Compute draw commands for this UI element and push them into renderer.draw_queue."""

        # if not self.render_interruption:
        #     return self.render_list

        self.render_interruption = False
        self.render_list = [
            self._build_draw_command(texture)
            for texture in self.draw
            if isinstance(texture, dict)
        ]

        return self.render_list

    def _build_draw_command(self, texture: dict) -> dict:
        """Create a render dictionary for a single texture entry."""

        draw_dict = self.dict["defaults"]["draw"] | texture

        # get texture file
        if "file" in draw_dict:
            color_texture = draw_dict["file"]
        else:
            folder = draw_dict["folder"]
            color_texture = folder + "/" + draw_dict.get("name", "")

        texture_aspect = color_texture
        flip = draw_dict["flip"]

        # compute shake & draw_dict position
        shake_offset = numpy.array(self.draw_shake.update(0.16), dtype=numpy.float32)[
            :2
        ]
        texture_offset = numpy.array(
            draw_dict["position"],
            dtype=numpy.float32,
        )
        position = self.position + rotate_vector_2d(
            self.rotation, shake_offset + texture_offset[:2]
        )
        size = self.scale * numpy.array(draw_dict["size"], dtype=numpy.float32)
        if "meter" in draw_dict:
            meter = draw_dict["meter"]
            meter_value = (
                self.parent.meters[meter] / self.parent.dict["meters"][meter]["max"]
            )

            size *= numpy.array([meter_value, 1], dtype=numpy.float32)

        rotation = self.rotation + numpy.array(
            draw_dict["rotation"],
            dtype=numpy.float32,
        )

        x_flip = flip[0]
        if draw_dict["side"]:
            x_flip = not x_flip if self.side == ScreenSide.RIGHT else x_flip

        # build final render dictionary
        return draw_dict | {
            "color_texture": color_texture,
            "position": position,
            "size": size[:2],
            "rotation": rotation,
            "texture_aspect": texture_aspect,
            "side": self.side == ScreenSide.RIGHT,
            "flip": [x_flip, flip[1]],
            "shadow_cast": False,
        }
