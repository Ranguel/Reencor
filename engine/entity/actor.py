import numpy

from engine.entity.base import Base
from engine.constant.physics import *
from engine.constant.combat import *
from engine.constant.entity import *
from engine.math.vector import rotate_vector


class Actor(Base):
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
        self.type = EntityType.ACTOR
        self.subtype = EntitySubtype.FIGHTER

        self.mass = self.dict["mass"]
        self.speed = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.acceleration = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.gravity = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.con_speed = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.grounded = False
        self.air_time = 0
        self.air_max_height = 0

        self.meters = {
            meter: self.dict["meters"][meter]["inicial"]
            for meter in self.dict["meters"]
        }

        self.kara = 0
        self.hitstun = 0
        self.hitreg = {box: set() for box in self.dict["defaults"]["boxes"]}
        self.attack_id = 0

        self.guard = [GuardState.IDLE, 0]
        self.juggle = 100
        self.wallbounce = False
        self.influence_object = None

        self.last_position = numpy.array(self.position, dtype=numpy.float32)
        self.last_rotation = numpy.array(self.rotation, dtype=numpy.float32)
        self.last_scale = numpy.array(self.scale, dtype=numpy.float32)

        super().inicial_state(state=state)

    def _meter_update(self):
        for meter in self.meters:
            if self.meters[meter] < 0:
                self.meters[meter] = 0
            if self.meters[meter] > self.dict["meters"][meter]["max"]:
                self.meters[meter] = self.dict["meters"][meter]["max"]

    def _hitstun_update(self):
        if self.kara:
            self.kara -= 1

        if (
            self.hitstop == 0
            and self.grabed == None
            and self.hitstun > 0
            and self.boxes["hurtbox"].get("condition", "") != "tumble"
        ):
            self.hitstun -= 1

    def _physics_update(self):
        if (not self.hitstop) and (self.grabed == None):
            self.speed += (
                self.acceleration
                + rotate_vector(self.rotation, self.con_speed)
                + self.gravity
            ) * self.scale

            self.position += self.speed

    def _transform_iterruption(self):
        if (
            numpy.any(self.position != self.last_position)
            or numpy.any(self.rotation != self.last_rotation)
            or numpy.any(self.scale != self.last_scale)
        ):
            self.render_interruption = True

        self.last_position = numpy.array(self.position, dtype=numpy.float32)
        self.last_rotation = numpy.array(self.rotation, dtype=numpy.float32)
        self.last_scale = numpy.array(self.scale, dtype=numpy.float32)

    def update(self, **kwargs):
        super().update(**kwargs)
        self._meter_update()
        self._hitstun_update()
        self._physics_update()
        self._transform_iterruption()
