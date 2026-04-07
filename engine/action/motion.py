import numpy

from engine.math.vector import normalize_length, rotate_vector


def set_facing(self: object, value=1, **kwargs):
    """Set the direction in which the object is facing. 'Facing': -1 reverses the direction the object is currently facing"""
    self.rotation[0] = 0 if value == 1 else 180


def apply_position_offset(self: object, value={"vec": [0, 0]}, **kwargs):
    """Changes the location of the object instantly. Does not affect speed. 'Pos_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.position += (
        rotate_vector(
            self.rotation,
            normalize_length(value["vec"]),
        )
        * self.scale
    )


def apply_pushback(self: object, value=[0, 0], **kwargs):
    """Changes the location of the object instantly. Does not affect speed. 'Pos_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.position += normalize_length(value)


def apply_velocity(
    self: object, value: dict = {"vec": [0, 0], "type": "set"}, **kwargs
):
    """Set the absolute Speed of the object. 'Speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    if value.get("type", "set") == "set":
        self.speed = (
            rotate_vector(self.rotation, normalize_length(value.get("vec", [0, 0])))
            * self.scale
        )
    elif value.get("type", "") == "add":
        self.speed += (
            rotate_vector(self.rotation, normalize_length(value.get("vec", [0, 0])))
            * self.scale
        )
    elif value.get("type", "") == "constant":
        self.con_speed = (
            numpy.array(
                normalize_length(value.get("vec", [0, 0])),
                dtype=numpy.float32,
            )
            * self.scale
        )


def apply_acceleration(self: object, value={"vec": [0, 0]}, **kwargs):
    """Set the Acceleration of the object. 'Accel': (X Acceleration (Depends on where the object is facing)., Y Acceleration)"""
    self.acceleration = (
        rotate_vector(self.rotation, normalize_length(value["vec"])) * self.scale
    )


def apply_gravity(self: object, value={"vec": [0, -0.1]}, **kwargs):
    """Set the Gravity of the object. 'Gravity': (X Gravity (Depends on where the object is facing)., Y Gravity)"""
    self.gravity = (
        numpy.array(normalize_length(value["vec"]), dtype=numpy.float32) * self.scale
    )


def set_influence_target(self: object, value: str = "", other=object, **kwargs):
    if value == "other":
        self.object_influence, other.grabed = other, self


def update_influence_position(self, value: list = [10, 10, 10], **kwargs):
    if self.object_influence != None:
        self.object_influence.position = self.position + rotate_vector(
            self.rotation, value if len(value) == 3 else (value[0], value[1], 0)
        )


def update_influence_velocity(self, value: list = [10, 10], **kwargs):
    if self.object_influence != None:
        self.object_influence.speed = [value[0], value[1], 0]


def clear_influence(self: object, **kwargs):
    self.object_influence.grabed = None
    self.object_influence = None


MOTION_ACT = {
    "facing": set_facing,
    "speed": apply_velocity,
    "accel": apply_acceleration,
    "gravity": apply_gravity,
    "pos_offset": apply_position_offset,
    "pushback": apply_pushback,
    "influence": set_influence_target,
    "influence_pos": update_influence_position,
    "influence_speed": update_influence_velocity,
    "off_influence": clear_influence,
}
