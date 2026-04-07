import math
import numpy


def round_sign(n):
    return int(1) if n > 0 else int(-1) if n < 0 else int(0)


def normalize_length(vector, length=3, fill=0.0):
    try:
        if isinstance(vector, numpy.ndarray):
            vector = vector.tolist()
        norm = vector[:length] + [fill] * max(0, length - len(vector))
        return numpy.array(norm, dtype=numpy.float32)
    except:
        return numpy.zeros(length, dtype=numpy.float32)


def normalize_vector(x, y, base=1):
    magnitude = math.sqrt(x**2 + y**2)
    if magnitude == 0:
        return [0, 1 * base]
    return [x / magnitude * base, y / magnitude * base]


def rotate_vector(angle, vector):
    cx, cy, cz = numpy.cos(numpy.radians(angle))
    sx, sy, sz = numpy.sin(numpy.radians(angle))

    return (
        numpy.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        @ numpy.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        @ numpy.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    ) @ numpy.array(vector, dtype=numpy.float32)


def rotate_vector_2d(angle, vector):
    angle = numpy.radians(angle)
    c, s = numpy.cos(angle), numpy.sin(angle)
    try:
        x, y = vector
    except:
        print(f"Error rotating vector: {vector} is not a valid 2D vector.")

    return numpy.array((x * c - y * s, x * s + y * c), dtype=numpy.float32)
