import numpy

from engine.id.entity import EntityIdGenerator
from engine.constant.physics import *
from engine.constant.ui import *
from engine.math.vector import rotate_vector_2d
from engine.math.geometry import find_object_by_direccional_input
from engine.physics.transform import (
    get_world_position,
    get_world_scale,
    get_world_rotation,
)
from engine.effect.shake import ShakeComponent
from engine.action.state import build_state_buffer, find_next_state, trigger_state
from engine.gameplay.object_hierarchy import children_set_attribute, children_kill


class Selector:
    def __init__(
        self,
        dict: dict = {},
        color: list = [1, 1, 1, 1],
        state: str = "none",
        condition: set = set(),
        position: numpy.array = numpy.array([0, 0], dtype=numpy.float32),
        rotation: numpy.float32 = numpy.float32(0),
        scale: numpy.array = numpy.array([1, 1], dtype=numpy.float32),
        index: int = 0,
        items: list = [],
        life_time: bool = False,
    ):
        self.id = EntityIdGenerator.next()
        self.dict = dict
        self.type = UIType.SELECTOR
        self.subtype = UISubtype.LIFE
        self.color = color
        self.life_time = life_time if life_time else False

        self.dimension = 2
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.parent = None
        self.space = PositionSpace.LOCAL
        self.children = []
        self.index = index
        self.items = items

        self.draw = []
        self.render_list = []
        self.draw_shake = ShakeComponent()

        self.state_current = state
        self.state_buffer = {}
        self.state_data = []
        self.frame_data = {}

        self.frame_total = 0
        self.frame_duration = 0
        self.frame_index = 1
        self.frame_counter = 1
        self.frame_repeat = 0

        self.render_interruption = True
        self.frame_interruption = True
        self.state_interruption = True

        self.condition = set(condition)
        self.command = set()
        self.input = set({"x_neutral", "y_neutral"})
        self.input_device = None
        self.input_interruption = False

        self.selected = None
        self.selected_timer = 20

        self.inicial_state(state=state)

    def inicial_state(self, state):
        if state != "none":
            state_found = find_next_state(self, state_buffer={state: 2}, force=True)

    def _flag_update(self):
        if self.render_interruption:
            self.render_interruption = False

        if self.frame_interruption:
            self.frame_interruption = False

        if self.state_interruption:
            self.state_interruption = False

        if self.draw_shake.active:
            self.render_interruption = True

    def _selector_update(self):
        direction = [
            (
                1
                if "left_press" in self.input
                else -1 if "right_press" in self.input else 0
            ),
            1 if "up_press" in self.input else -1 if "down_press" in self.input else 0,
        ]

        if "A_press" in self.input:
            trigger_state(self, "selected")
            self.selected = self.items[self.index]

        if "B_press" in self.input:
            trigger_state(self, "idle")
            self.selected = None

        if self.selected != None:
            self.selected_timer -= 1

        if self.selected == None:
            if self.selected_timer != 20:
                self.selected_timer = 20
            if direction != [0, 0]:
                self.index = find_object_by_direccional_input(
                    index=self.index, items=self.items, direction=direction
                )

    def _buffer_update(self):
        self.state_buffer = {
            timer: self.state_buffer[timer] - 1
            for timer in self.state_buffer
            if self.state_buffer[timer] > 0
        }

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

    def _frame_update(self):
        self.frame_counter += 1
        if (
            self.frame_counter >= self.frame_duration
            and self.frame_index < self.frame_total
        ) and self.state_current != "none":
            self.frame_interruption = True
            self.frame_data = self.state_data[self.frame_index]
            self.frame_index += 1

    def _children_update(self):
        if self.children:
            if self.render_interruption:
                children_set_attribute(
                    self=self, attribute="render_interruption", value=1
                )
            if self.state_interruption:
                children_kill(self=self, state_interruption=self.state_interruption)

    def _world_position_update(self):
        self.parent = self.items[self.index]
        self.world_position = get_world_position(self=self)
        self.world_scale = get_world_scale(self=self)
        self.world_rotation = get_world_rotation(self=self)

    def _life_time_update(self):
        """Update life timer and mark for deletion if expired."""

        if isinstance(self.life_time, int) and not isinstance(self.life_time, bool):
            self.life_time -= 1

    def update(self, **kwargs):
        self._flag_update()
        self._selector_update()
        self._buffer_update()
        self._state_update()
        self._frame_update()
        self._children_update()
        self._world_position_update()
        self._life_time_update()

    def render(self, **kwargs) -> list:
        """Compute draw commands for this UI element and push them into renderer.draw_queue."""

        if not self.render_interruption:
            return self.render_list

        self.render_interruption = False
        self.render_list = [
            self._build_draw_command(texture)
            for texture in self.draw
            if isinstance(texture, dict)
        ]

        return self.render_list

    def _build_draw_command(self, texture: dict) -> dict:
        """Create a render dictionary for a single texture entry."""

        defaults = self.dict["defaults"]["draw"]

        # get texture file
        if "file" in texture:
            color_texture = texture["file"]
        else:
            color_texture = (
                texture.get("folder", defaults["folder"])
                + "/"
                + texture.get("name", "")
            )
        texture_aspect = color_texture
        flip = texture.get("flip", self.dict["defaults"]["draw"]["flip"])

        # compute shake & texture position
        shake_offset = numpy.array(self.draw_shake.update(0.16), dtype=numpy.float32)[
            :2
        ]
        texture_offset = numpy.array(
            texture.get("position", defaults["position"]),
            dtype=numpy.float32,
        )[:2]
        position = self.world_position + rotate_vector_2d(
            self.world_rotation, shake_offset + (texture_offset * self.world_scale)
        )
        size = self.world_scale * numpy.array(
            texture.get("size", defaults["size"][:2]), dtype=numpy.float32
        )
        rotation = self.world_rotation + numpy.array(
            texture.get("rotation", defaults["rotation"])[0],
            dtype=numpy.float32,
        )

        x_flip = flip[0]
        if texture.get("side", defaults["side"]):
            x_flip = not x_flip if self.side == ScreenSide.RIGHT else x_flip

        # build final render dictionary
        return {
            "color_texture": color_texture,
            "position": position,
            "size": size[:2],
            "rotation": rotation,
            "texture_aspect": texture_aspect,
            "keep_aspect": texture.get("keep_aspect", defaults["keep_aspect"]),
            "side": False,
            "flip": [x_flip, flip[1]],
            "tint": texture.get("tint", defaults["tint"]),
            "glow": texture.get("glow", defaults["glow"]),
            "uv_scale": texture.get("uv_scale", defaults["uv_scale"]),
            "uv_offset": texture.get("uv_offset", defaults["uv_offset"]),
            "uv_size": texture.get("uv_size", defaults["uv_size"]),
            "program": texture.get("program", defaults["program"]),
        }
