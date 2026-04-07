from enum import Enum, auto


class UIType(Enum):
    CARD = auto()
    SELECTOR = auto()
    MENU = auto()
    INDICATOR = auto()
    LABEL = auto()


class UISubtype(Enum):
    TIME = auto()
    LIFE = auto()
    SUPER = auto()
    DAMAGE = auto()
    COMBO = auto()
    COMBO_DAMAGE = auto()
    SCALING = auto()
    COUNTER = auto()
    GUARD = auto()


class ScreenSide(Enum):
    RIGHT = True
    LEFT = False


class Textindent(Enum):
    RIGHT = auto()
    LEFT = auto()
    CENTER = auto()
