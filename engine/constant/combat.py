from enum import Enum, IntEnum, auto


BOXES_COLORS = {
    "hurtbox": (0.1, 0.1, 1, 1),
    "hitbox": (1, 0.1, 0.1, 1),
    "takebox": (0.1, 1, 1, 1),
    "grabbox": (0.1, 1, 0.1, 1),
    "pushbox": (1, 0, 1, 1),
    "triggerbox": (1, 0.5, 0, 1),
    "environmentbox": (1, 1, 1, 1),
}


class AttackLevel(IntEnum):
    LOW = 1
    MID = 2
    HIGH = 3


class AttackStrength(IntEnum):
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3
    SPECIAL = 4
    SUPER = 5


class AttackType(IntEnum):
    NORMAL = 1
    SPECIAL = 2
    SUPER = 3


class HitResult(IntEnum):
    WHIFF = 0
    HIT = 1
    BLOCK = 2
    PARRY = 3


ATTACK_SCALING = {
    AttackStrength.SUPER: {"scaling": 0.10, "min": 0.50},
    AttackStrength.SPECIAL: {"scaling": 0.10, "min": 0.20},
    AttackStrength.LIGHT: {"scaling": 0.08, "min": 0.10},
    AttackStrength.MEDIUM: {"scaling": 0.09, "min": 0.10},
    AttackStrength.HEAVY: {"scaling": 0.10, "min": 0.10},
}


class AttackReaction(IntEnum):
    NONE = 0
    JAW = 1
    UPPERCUT = 2
    SOLARPLEX = 3
    BODY = 4
    HOOK = 5
    TRIP = 6
    TURN = 7
    OVERHEAD = 8


class GuardOutcome(Enum):
    NONE = auto()

    BLOCK_HIGH = auto()
    BLOCK_LOW = auto()
    HIGH_ON_LOW_BLOCK = auto()
    LOW_ON_HIGH_BLOCK = auto()

    PARRY_HIGH = auto()
    PARRY_LOW = auto()
    HIGH_ON_LOW_PARRY = auto()
    LOW_ON_HIGH_PARRY = auto()


class CounterResult(Enum):
    NONE = auto()
    INTERRUPT = auto()
    TRADE = auto()
    PUNISH = auto()


class CounterCause(Enum):
    CATCH = auto()
    REACH = auto()


class GuardState(Enum):
    IDLE = auto()
    BLOCK = auto()
    PARRY = auto()
