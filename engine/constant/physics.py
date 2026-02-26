from enum import Enum


class BodyType(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"


class PositionSpace(Enum):
    LOCAL = "local"
    GLOBAL = "global"
