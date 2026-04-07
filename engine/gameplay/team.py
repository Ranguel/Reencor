from engine.constant.ui import *


class Team:
    def __init__(
        self, index: int = 0, main: object = None, side: ScreenSide = ScreenSide.LEFT
    ):
        self.index = index
        self.side = side
        self.main = main
        self.members = [main] if main else []

        self.indicators = []
        self.labels = []

        self.combo = 0

        self.combo_list = []
        self.damage_scaling = 1
        self.last_damage = 0
        self.combo_damage = 0
