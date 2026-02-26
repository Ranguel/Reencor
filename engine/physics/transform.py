import numpy
from engine.constant.physics import *


class Transform:
    def __init__(
        self,
        position: numpy.array = numpy.zeros(3, dtype=numpy.float32),
        rotation: numpy.array = numpy.zeros(3, dtype=numpy.float32),
        scale: numpy.array = numpy.ones(3, dtype=numpy.float32),
        parent: object = None,
    ):
        (
            self.position,
            self.rotation,
            self.scale,
            self.parent,
        ) = (
            position,
            rotation,
            scale,
            parent,
        )

        self.last_position = position
        self.last_rotation = rotation
        self.last_scale = scale

    def get_world_position(self):
        if self.parent:
            return self.parent.transform.get_world_position() + self.position
        return self.position


def get_world_position(self):
    if self.parent and self.space == PositionSpace.LOCAL:
        return get_world_position(self.parent) + self.position
    return self.position

def get_world_scale(self):
    if self.parent and self.space == PositionSpace.LOCAL:
        return get_world_scale(self.parent) * self.scale
    return self.scale

def get_world_rotation(self):
    if self.parent and self.space == PositionSpace.LOCAL:
        return get_world_rotation(self.parent) + self.rotation
    return self.rotation
