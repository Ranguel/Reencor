import numpy

from engine.gameplay.common_functions import (
    get_state,
    get_substate,
    get_command,
    object_get_state,
    object_kill,
    rotatate_vector,
    normalize_length,
)
from engine.effects.shake import ShakeComponent


def meter_indicator_length(value: float, max_value: float) -> float:
    return value / max_value


class Menu_Item:
    def __init__(
        self,
        game: object = object,
        dict: dict = {},
        position: numpy.array = numpy.array([0, 0, 0], dtype=numpy.float32),
        scale: numpy.array = numpy.array([1, 1, 1], dtype=numpy.float32),
        rotation: numpy.array = numpy.array([0, 0, 0], dtype=numpy.float32),
        state: str = "none",
        condition: set = {},
        palette: int = 0,
        side: bool = False,
        parent: object = None,
    ):
        (
            self.app,
            self.type,
            self.dict,
            self.position,
            self.scale,
            self.rotation,
            self.palette,
            self.side,
            self.parent,
        ) = (
            game,
            dict.get("type", "menu_item").casefold(),
            dict,
            position,
            scale,
            rotation,
            palette,
            side,
            parent if parent != None else self,
        )
        (
            self.draw,
            self.draw_shake,
        ) = (
            [],
            ShakeComponent(),
        )
        self.time_kill = False

        (
            self.frame,
            self.repeat_substate,
        ) = ([0, 0], 0)
        (
            self.speed,
            self.acceleration,
            self.gravity,
        ) = (
            numpy.array([0, 0, 0], dtype=numpy.float32),
            numpy.array([0, 0, 0], dtype=numpy.float32),
            numpy.array([0, 0, 0], dtype=numpy.float32),
        )
        (
            self.grounded,
            self.cancel,
            self.state_current,
            self.current_condition,
            self.state_buffer,
        ) = (False, set(), state, set(condition), {})

        self.move_raw_input = {
            move: []
            for move in self.dict["states"]
            if self.dict["states"][move].get("command", False)
        }
        self.input_interruption = False
        self.input = {"x_neutral", "y_neutral"}
        self.command = {""}

        self.pending_changes = {}

        if state == "none":
            object_get_state(self, value={"force": True})
        else:
            get_state(self, {state: 2}, 1)
            get_substate(self, self.dict["states"][self.state_current]["framedata"][0])

        self.last_position = numpy.array(self.position, dtype=numpy.float32)
        self.last_rotation = numpy.array(self.rotation, dtype=numpy.float32)
        self.last_scale = numpy.array(self.scale, dtype=numpy.float32)

        self.render_interruption = True
        self.render_list = []

    def update(self, *args):
        self.speed += self.acceleration + self.gravity
        self.position += self.speed

        self.state_buffer = {
            timer: self.state_buffer[timer] - 1
            for timer in self.state_buffer
            if self.state_buffer[timer] > 0
        }

        if self.input_interruption or (self.frame[0] <= 0 and self.frame[1] <= 0):
            get_command(self, current_condition=self.input | self.current_condition)

        if self.frame[0] <= 0 and self.frame[1] <= 0:
            get_state(self, self.state_buffer)

        self.frame[1] -= 1
        if self.frame[1] <= 0:
            get_substate(
                self,
                self.dict["states"][self.state_current]["framedata"][-self.frame[0]],
            )

        self.input_interruption = False
        self.current_condition.clear()

        if type(self.time_kill) != bool:
            self.time_kill -= 1
            if self.time_kill == 0:
                object_kill(self)

        if (
            numpy.any(self.position != self.last_position)
            or numpy.any(self.rotation != self.last_rotation)
            or numpy.any(self.scale != self.last_scale)
            or 1
        ):
            self.render_interruption = True

        self.last_position = numpy.array(self.position, dtype=numpy.float32)
        self.last_rotation = numpy.array(self.rotation, dtype=numpy.float32)
        self.last_scale = numpy.array(self.scale, dtype=numpy.float32)

    def render(self, renderer, *args):
        """Compute draw commands for this UI element and push them into renderer.draw_queue."""

        if not self.render_interruption:
            renderer.draw_queue.extend(self.render_list)
            return

        self.render_interruption = False
        self.render_list = [self._build_draw_command(texture) for texture in self.draw]

        renderer.draw_queue.extend(self.render_list)

    def _build_draw_command(self, texture: dict) -> dict:
        """Create a render dictionary for a single texture entry."""

        file = texture.get("file", "")
        flip = texture.get("flip", self.dict["defaults"]["draw"]["flip"])
        defaults = self.dict["defaults"]["draw"]

        # get texture file or fallback
        image_file = self.app.image_dict.get(file, self.app.image_dict["reencor/none"])
        texture_data, texture_size = image_file

        # compute shake & texture offset
        shake_offset = numpy.array(self.draw_shake.update(0.16), dtype=numpy.float32)
        texture_offset = numpy.array(
            normalize_length(texture.get("position", defaults["position"])),
            dtype=numpy.float32,
        )

        # compute position
        position = (
            self.position
            + rotatate_vector(self.rotation, shake_offset + texture_offset)
        )[:2]

        # compute size and scaling (with meter support)
        size = self.scale * numpy.array(
            normalize_length(texture.get("size", defaults["size"])), dtype=numpy.float32
        )
        if texture.get("meter", False):
            meter = texture["meter"]
            meter_value = meter_indicator_length(
                self.parent.meters[meter], self.parent.dict["meters"][meter]["max"]
            )
            size *= numpy.array([meter_value, 1, 1], dtype=numpy.float32)

        # compute rotation
        rotation = self.rotation + numpy.array(
            normalize_length(texture.get("rotation", defaults["rotation"])),
            dtype=numpy.float32,
        )

        # compute flip (mirror by side)
        x_flip = flip[0]
        if texture.get("side", defaults["side"]):
            x_flip = not x_flip if self.side else x_flip

        return {
            "color_texture": texture_data,
            "position": position,
            "size": size[:2],
            "rotation": rotation,
            "texture_aspect": texture_size[0] / texture_size[1],
            "keep_aspect": texture.get("keep_aspect", defaults["keep_aspect"]),
            "side": self.side,
            "flip": [x_flip, flip[1]],
            "tint": texture.get("tint", defaults["tint"]),
            "glow": texture.get("glow", defaults["glow"]),
            "uv_scale": texture.get("uv_scale", defaults["uv_scale"]),
            "uv_offset": texture.get("uv_offset", defaults["uv_offset"]),
            "uv_size": texture.get("uv_size", defaults["uv_size"]),
            "program": texture.get("program", defaults["program"]),
        }

    def draw_boxes(self):
        pass
