import numpy

from engine.entity.visual import Visual
from engine.id.entity import EntityIdGenerator
from engine.constant.physics import *
from engine.constant.entity import *
from engine.constant.combat import BOXES_COLORS
from engine.math.vector import rotate_vector
from engine.math.matrix import get_model_matrix
from engine.action.state import build_state_buffer, find_next_state


class Base(Visual):
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
        super().__init__(
            dict=dict,
            palette=palette,
            state=state,
            condition=condition,
            parent=parent,
            space=space,
            position=position,
            rotation=rotation,
            scale=scale,
            life_time=life_time,
        )
        self.type = EntityType.BASE
        self.subtype = EntitySubtype.STAGE

        self.boxes = {}
        self.grabed = None
        self.cancel = set([None])
        self.hitstop = 0
        self.pending_changes = {}

        self.command = set()
        self.input = set({"x_neutral", "y_neutral"})
        self.input_device = None
        self.input_interruption = False

        super().inicial_state(state=state)

    def _buffer_update(self):
        if (not self.hitstop) and (self.grabed == None):
            self.state_buffer = {
                timer: self.state_buffer[timer] - 1
                for timer in self.state_buffer
                if self.state_buffer[timer] > 0
            }
        if (
            self.input_interruption
            or (
                self.frame_index >= self.frame_total
                and self.frame_counter >= self.frame_duration
            )
            or (self.cancel.isdisjoint([None]))
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

    def _hitstop_update(self):
        if self.hitstop:
            self.hitstop -= 1

    def _frame_update(self):
        if not self.hitstop:
            self.frame_counter += 1
        if (
            self.frame_counter >= self.frame_duration
            and self.frame_index < self.frame_total
        ) and self.state_current != "none":
            self.frame_interruption = True
            self.frame_data = self.state_data[self.frame_index]
            self.frame_index += 1

    def update(self, **kwargs):
        self._hitstop_update()
        super().update(**kwargs)

    def draw_boxes(self) -> list:
        boxes_list = []
        for boxes_type in self.boxes:
            for box in self.boxes[boxes_type].get("rects", []):
                size = (
                    box["vec"][2] * self.scale[0],
                    box["vec"][3] * self.scale[1],
                )
                model = get_model_matrix(
                    position=self.position
                    + rotate_vector(
                        self.rotation,
                        numpy.array(
                            (box["vec"][0], box["vec"][1], 0),
                            dtype=numpy.float32,
                        ),
                    )
                    * self.scale,
                    size=size,
                    rotation=self.rotation,
                )

                render_cmd = {
                    "model": model,
                    "color": BOXES_COLORS[boxes_type],
                    "transparent": 0.1,
                    "size": size,
                    "border_thickness": 0.02,
                    "disable_depth_test": True,
                    "program": "box",
                }

                boxes_list.append(render_cmd)

        return boxes_list
