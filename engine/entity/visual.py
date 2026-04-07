import numpy

from engine.id.entity import EntityIdGenerator
from engine.constant.physics import *
from engine.constant.entity import *
from engine.math.vector import normalize_length, rotate_vector
from engine.math.matrix import get_model_matrix
from engine.physics.transform import (
    get_world_position,
    get_world_scale,
    get_world_rotation,
)
from engine.effect.shake import ShakeComponent
from engine.action.state import build_state_buffer, find_next_state
from engine.gameplay.object_hierarchy import children_set_attribute, children_kill


class Visual:
    def __init__(
        self,
        dict: dict = {},
        palette: int = 0,
        state: str = "none",
        condition: set = set(),
        parent: object = None,
        space: PositionSpace = PositionSpace.GLOBAL,
        position: numpy.array = numpy.array([0, 0, 0], dtype=numpy.float32),
        rotation: numpy.array = numpy.array([0, 0, 0], dtype=numpy.float32),
        scale: numpy.array = numpy.array([1, 1, 1], dtype=numpy.float32),
        life_time: bool = False,
    ):
        self.id = EntityIdGenerator.next()
        self.type = EntityType.VISUAL_EFFECT
        self.subtype = EntitySubtype.SPARK
        self.dict = dict
        self.palette = palette
        self.life_time = life_time if life_time else self.dict.get("timekill", False)

        self.dimension = 3
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.parent = parent
        self.space = space
        self.children = []

        self.draw = []
        self.render_list = []
        self.draw_shake = ShakeComponent()

        self.sound = []
        self.sound_list = []

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

    def _buffer_update(self):
        self.state_buffer = {
            timer: self.state_buffer[timer] - 1
            for timer in self.state_buffer
            if self.state_buffer[timer] > 0
        }

        if (
            self.frame_index >= self.frame_total
            and self.frame_counter >= self.frame_duration
            and self.frame_counter >= self.frame_duration
        ):
            build_state_buffer(
                self,
                current_condition=self.condition,
            )

    def _state_update(self):
        if self.state_buffer or (
            self.frame_index >= self.frame_total
            and self.frame_counter >= self.frame_duration
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
        self.world_position = get_world_position(self=self)
        self.world_scale = get_world_scale(self=self)
        self.world_rotation = get_world_rotation(self=self)

    def _life_time_update(self):
        """Update life timer and mark for deletion if expired."""

        if isinstance(self.life_time, int) and not isinstance(self.life_time, bool):
            self.life_time -= 1

    def update(self, **kwargs):
        self._flag_update()
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

        # compute shake & texture position
        shake_offset = numpy.array(self.draw_shake.update(0.016), dtype=numpy.float32)
        texture_offset = numpy.array(
            normalize_length(draw_dict["position"]),
            dtype=numpy.float32,
        )

        # generate model matrix
        position = self.world_position + rotate_vector(
            self.world_rotation, shake_offset + (texture_offset * self.world_scale)
        )
        size = self.world_scale * numpy.array(
            normalize_length(draw_dict["size"]),
            dtype=numpy.float32,
        )
        rotation = self.world_rotation + numpy.array(
            normalize_length(draw_dict["rotation"]),
            dtype=numpy.float32,
        )
        model = get_model_matrix(position=position, size=size, rotation=rotation)

        # build final render dictionary
        return draw_dict | {
            "color_texture": color_texture,
            "model": model,
        }

    def audio(self, **kwargs) -> list:
        """Compute audio commands for this object and push them into soundsystem.audio_queue."""
        if not self.sound:
            return

        self.sound_list = [
            self._built_audio_command(sound)
            for sound in self.sound
            if isinstance(sound, dict)
        ]

        return self.sound_list

    def _built_audio_command(self, sound: dict) -> dict:
        sound = sound.get("file", "hit_heavy")
        volume = sound.get("volume", 1.0)
        pitch = sound.get("pitch", 1.0)
        balance = sound.get("balance", 0.0)

        return {
            "sound": sound,
            "volume": volume,
            "pitch": pitch,
            "balance": balance,
            "position": (0, 0),
        }
