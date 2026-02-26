import numpy

from engine.physics.transform import Transform
from engine.math.vector import rotate_vector
from engine.constant.physics import BodyType


class Motion:
    def __init__(self):
        self.velocity = numpy.zeros(3, dtype=numpy.float32)
        self.acceleration = numpy.zeros(3, dtype=numpy.float32)
        self.friction = numpy.zeros(3, dtype=numpy.float32)


class PhysicsBody:
    def __init__(self, body_type: str):
        self.type = body_type


class StaticBody(PhysicsBody):
    def __init__(self):
        super().__init__(BodyType.STATIC)


class DynamicBody(PhysicsBody):
    def __init__(
        self, gravity: numpy.array = numpy.zeros(3, dtype=numpy.float32), mass=1
    ):
        super().__init__(BodyType.DYNAMIC)

        self.linear = Motion()
        self.angular = Motion()
        self.scalar = Motion()
        self.gravity = gravity

        self.mass = mass

        self.enable = False
        self.enable_gravity = False
        self.enable_friction = True

    def integrate(self, transform=Transform, dt=0.016):
        if not self.enable:
            return

        self.linear.velocity += self.linear.acceleration * dt + self.gravity * dt
        self.linear.velocity *= self.linear.friction

        self.angular.velocity += self.angular.acceleration * dt
        self.angular.velocity *= self.angular.friction

        self.scalar.velocity += self.scalar.acceleration * dt
        self.scalar.velocity *= self.scalar.friction

        transform.position += self.linear.velocity
        transform.rotation += self.angular.velocity
        transform.scale += self.scalar.velocity
