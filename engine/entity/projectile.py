import numpy

from engine.entity.base import Base
from engine.constant.physics import *
from engine.constant.combat import *
from engine.constant.entity import *
from engine.math.vector import rotate_vector


class Projectile(Base):
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
        team: int = 0,
    ):
        super().__init__(
            dict=dict,
            palette=palette,
            state=state,
            condition=condition,
            parent=parent,
            space = space,
            position=position,
            rotation=rotation,
            scale=scale,
            life_time=life_time,
        )
        self.type = EntityType.PROJECTILE
        self.subtype = EntitySubtype.FIREBALL

        self.mass = self.dict["mass"]
        self.speed = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.acceleration = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.gravity = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.con_speed = numpy.array([0, 0, 0], dtype=numpy.float32)
        self.grounded = False

        self.hitreg = {box: set() for box in self.dict["defaults"]["boxes"]}
        self.attack_id = 0

        self.influence_object = None

        self.last_position = numpy.array(self.position, dtype=numpy.float32)
        self.last_rotation = numpy.array(self.rotation, dtype=numpy.float32)
        self.last_scale = numpy.array(self.scale, dtype=numpy.float32)

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

    def update(self, *args):
        super().update(*args)
        self._physics_update()
        self._transform_iterruption()
