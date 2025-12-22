from engine.gameplay.active_objects import BaseActiveObject
from engine.gameplay.interface_objects import Menu_Item


class BaseScreen:
    def __init__(self, game, *args):
        self.app = game
        game.cam_pos = [0, 3, 8]
        self.selected_stage_objects = []
        self.selected_character_objects = []
        self.indicators = []
        self.load_indicators = True

        self.app.show_boxes = False
        self.app.show_inputs = False
        self.app.show_ui = True

        self.load_objects(indicator=self.load_indicators)

    def load_objects(self, indicator=False, *args):
        self.app.active_stages = [
            BaseActiveObject(
                app=self.app,
                dict=self.app.object_dict[self.app.selected_stage[0]],
                state="Base",
            )
        ]

        self.app.active_players = [
            BaseActiveObject(
                app=self.app,
                dict=self.app.object_dict[self.app.selected_characters[0]],
                position=[-3, 0, 0],
                rotation=[0, 0, 0],
                team=1,
                side=False,
            ),
            BaseActiveObject(
                app=self.app,
                dict=self.app.object_dict[self.app.selected_characters[1]],
                position=[3, 0, 0],
                rotation=[0, 180, 0],
                team=2,
                side=True,
            ),
        ]

        if indicator:
            for active_object in self.app.active_players:
                for item_dict in active_object.dict.get("indicator", []):
                    if isinstance(item_dict, dict):
                        item_dict = item_dict.get("file", "")
                    if item_dict in self.app.object_dict:
                        self.indicators.append(
                            Menu_Item(
                                game=self.app,
                                dict=self.app.object_dict[item_dict],
                                position=(0, 0, 0),
                                state="Base",
                                side=active_object.side,
                                parent=active_object,
                            )
                        )

        self.app.object_list = (
            self.app.active_stages + self.app.active_players + self.indicators
        )

    def __loop__(self):
        pass

    def __dein__(self):
        pass


class IncialScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)

    def __loop__(self):
        super().__loop__()

    def __dein__(self):
        super().__dein__()


class DebuggingScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        # self.app.show_boxes = True
        # self.app.show_inputs = True

    def __loop__(self):
        super().__loop__()

        for active_object in self.app.active_players:
            if active_object.meters["health"] <= 0:
                active_object.meters["health"] = active_object.dict["meters"]["health"][
                    "max"
                ]

    def __dein__(self):
        super().__dein__()
        pass
