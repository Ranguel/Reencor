from enum import Enum, auto


class EntityType(Enum):
    BASE = auto()
    ACTOR = auto()
    PROJECTILE = auto()
    VISUAL_EFFECT = auto()

class EntitySubtype(Enum):
    STAGE = auto()
    FIGHTER = auto()
    FIREBALL = auto()
    PLATFORM = auto()
    REFLECTOR = auto()
    SPARK = auto()


