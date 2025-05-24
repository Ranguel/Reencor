from Util.Active_Objects import BaseActiveObject, reset_CharacterActiveObject
from Util.OpenGL_Renderer import draw_string
from Util.Common_functions import (
    function_dict,
    get_state,
    update_display_shake,
    weighted_choice,
    object_display_shake,
)
from Util.Interface_objects import (
    Menu_Item,
    Menu_Item_String,
    Menu_Selector,
    Menu_Cursor,
    Menu_Deck,
    Combo_Counter,
    Gauge_Bar,
    Message,
)
from Util.Box_Collitions import box_collide, calculate_boxes_collitions, draw_boxes


def load_objects(game, self, *args):
    game.active_stages = self.selected_stage_objects = [
        BaseActiveObject(
            game=game,
            dict=game.object_dict[game.selected_stage[0]],
            inicial_state="Stand",
        )
    ]
    game.active_players = self.selected_character_objects = [
        BaseActiveObject(
            game=game,
            dict=game.object_dict[game.selected_characters[0]],
            pos=(-300, -1),
            face=1,
            inputdevice=game.input_device_list[0],
            team=1,
        ),
        BaseActiveObject(
            game=game,
            dict=game.object_dict[game.selected_characters[1]],
            pos=(300, -1),
            face=-1,
            inputdevice=game.input_device_list[1] if len(game.input_device_list) > 1 else game.dummy_input_device,
            team=2,
        ),
    ]
    self.combo_counters = [
        Combo_Counter(game=game, parent=active_object)
        for active_object in self.selected_character_objects
    ]
    self.life_bars = [
        Gauge_Bar(
            game=game,
            dict=game.object_dict["Reencor/LifeBar"],
            parent=active_object,
        )
        for active_object in self.selected_character_objects
    ]
    self.super_bars = [
        Gauge_Bar(
            game=game,
            dict=game.object_dict["Reencor/SuperBar"],
            parent=active_object,
        )
        for active_object in self.selected_character_objects
    ]

    game.object_list = (
        self.selected_stage_objects
        + self.selected_character_objects
        + self.combo_counters
        + self.life_bars
        + self.super_bars
    )


class TitleScreen:
    def __init__(self, game, *args):
        self.game.object_list.append(0)

    def loop(self):
        pass


class ModeSelectionScreen:
    def __init__(self, game, *args):
        game.camera_focus_point = [0, 0, 400]
        self.game = game
        self.modes = {
            "Single Player": [VersusScreen, SinglePlayerCharacterSelectionScreen],
            "Multi Player": [VersusScreen, MultiPlayerCharacterSelectionScreen],
            "Trining": [TrainingScreen, SinglePlayerCharacterSelectionScreen],
            "Combo Trial": [ComboTrialScreen, SinglePlayerCharacterSelectionScreen],
            "Character Editor": [EditScreen, SinglePlayerCharacterSelectionScreen],
            "Debug": [DebuggingScreen],
        }
        self.mode_menu = [
            Menu_Item_String(
                game=game, name=mode, string=mode, pos=(-550, 250 - index * 100, 0)
            )
            for index, mode in enumerate(self.modes)
        ]
        self.menu_selectors = [
            Menu_Selector(
                game=game,
                inputdevice=game.input_device_list[0],
                menu=self.mode_menu,
                index=0,
            )
        ]
        self.selection_timer = 60

    def __loop__(self):
        for mode in self.mode_menu:
            mode.update(self.game.camera_focus_point)
            mode.draw(self.game.screen, self.game.camera.pos)
        for selector in self.menu_selectors:
            selector.update(self.game.camera_focus_point)
            selector.draw(self.game.screen, self.game.camera.pos)
        if not (None in [selected.selected_name for selected in self.menu_selectors]):
            self.selection_timer -= 1
            if self.selection_timer == 0:
                self.game.active = False
        else:
            self.selection_timer = 120

    def __dein__(self):
        self.game.screen_sequence += self.modes[self.menu_selectors[0].selected_name]


class SinglePlayerCharacterSelectionScreen:
    def __init__(self, game, *args):
        game.camera_focus_point = [0, 0, 400]
        self.game = game

        self.character_found = [
            key
            for key in self.game.object_dict.keys()
            if self.game.object_dict[key]["type"] == "character"
        ] * 5
        self.menu_character = [
            Menu_Item(
                game,
                name=self.character_found[index],
                image=game.object_dict[self.character_found[index]]["portrait"],
                pos=(
                    -360
                    + (index - int(index / 4) * 4) * 145
                    + (int(int(index / 6) % 2 == 0) * 20),
                    200 - int(index / 4) * 115,
                    0,
                ),
                size=(140, 110),
            )
            for index in range(len(self.character_found))
        ]
        self.menu_selectors = [
            Menu_Selector(
                game=game,
                team=ind + 1,
                inputdevice=game.input_device_list[ind],
                menu=self.menu_character,
                index=ind,
            )
            for ind in range(len(game.input_device_list))
        ]
        self.dummy_list = [
            BaseActiveObject(
                game=game,
                dict=game.object_dict[game.selected_characters[0]],
                face=1 if ind == 0 else -1,
                inputdevice=game.dummy_input_device,
                team=ind + 1,
            )
            for ind in range(len(game.input_device_list))
        ]
        self.dummy_list[0].other_main_object, self.dummy_list[0].face = (
            self.dummy_list[1],
            1,
        )
        self.dummy_list[1].other_main_object, self.dummy_list[1].face = (
            self.dummy_list[0],
            -1,
        )

        self.selection_timer = 60

    def __loop__(self):
        for character in self.menu_character:
            character.update(self.game.camera_focus_point)
            character.draw(self.game.screen, self.game.camera.pos)
        for selector in self.menu_selectors:
            selector.update(self.game.camera_focus_point)
            selector.draw(self.game.screen, self.game.camera.pos)
            if selector.index_int:
                reset_CharacterActiveObject(
                    self=self.dummy_list[selector.team - 1],
                    game=self.game,
                    dict=self.game.object_dict[
                        selector.menu[selector.selected_index].name
                    ],
                    face=1 if selector.team == 1 else -1,
                    team=self.dummy_list[selector.team - 1].team,
                    inputdevice=self.game.dummy_input_device,
                )

            if selector.selected and selector.select_int == 1:
                self.dummy_list[selector.team - 1].current_command.append("victorious")
            if selector.select_int == -1:
                get_state(self.dummy_list[selector.team - 1], {"Stand": 2}, True)

        for dummy in self.dummy_list:
            dummy.update(self.game.camera_focus_point)
            dummy.fet = "grounded"
            dummy.pos = [-450, -200, 50] if dummy.team == 1 else [450, -200, 50]
            dummy.draw(self.game.screen, self.game.camera.pos)

        if self.menu_selectors[0].selected and self.menu_selectors[0].select_int == 1:
            self.menu_selectors[1].inputdevice = self.game.input_device_list[0]
            self.menu_selectors[0].inputdevice = self.game.input_device_list[1]
        if (
            self.menu_selectors[1].selected == False
            and self.menu_selectors[1].select_int == -1
        ):
            self.menu_selectors[1].inputdevice = self.game.input_device_list[1]
            self.menu_selectors[0].inputdevice = self.game.input_device_list[0]
            self.menu_selectors[0].on_deselection(), self.menu_selectors[
                1
            ].on_deselection()

        if not (None in [selected.selected_name for selected in self.menu_selectors]):
            self.selection_timer -= 1
            if self.selection_timer == 0:
                self.game.active = False
        else:
            self.selection_timer = 120

    def __dein__(self):
        self.game.selected_characters = [
            selected.selected_name for selected in self.menu_selectors
        ]
        self.game.selected_stage = ["Reencor/Training"]


class MultiPlayerCharacterSelectionScreen:
    def __init__(self, game, *args):
        game.camera_focus_point = [0, 0, -400]
        self.game = game
        self.character_found = [
            key
            for key in self.game.object_dict.keys()
            if self.game.object_dict[key]["type"] == "character"
        ] * 5
        self.menu_character = [
            Menu_Item(
                self.character_found[index],
                (
                    360
                    + (index - int(index / 4) * 4) * 145
                    + (int(int(index / 6) % 2 == 0) * 20),
                    40 + int(index / 4) * 115,
                    0,
                ),
                (140, 110),
            )
            for index in range(len(self.character_found))
        ]
        self.menu_selectors = [
            Menu_Selector(
                ind + 1, game.input_device_list[ind], self.menu_character, ind
            )
            for ind in range(len(game.input_device_list))
        ]
        self.dummy_list = [
            BaseActiveObject(
                game,
                ind + 1,
                game.dummy_input_device,
                self.character_found[ind],
                (0, 0, 0),
                1,
                ind + 1,
            )
            for ind in range(len(game.input_device_list))
        ]
        self.dummy_list[0].other_main_object, self.dummy_list[0].face = (
            self.dummy_list[1],
            1,
        )
        self.dummy_list[1].other_main_object, self.dummy_list[1].face = (
            self.dummy_list[0],
            -1,
        )
        self.selection_timer = 60

    def __loop__(self):
        for character in self.menu_character:
            character.update(self.game.camera_focus_point)
            character.draw(self.game.screen, self.game.camera.pos)
        for selector in self.menu_selectors:
            selector.update(self.game.camera_focus_point)
            selector.draw(self.game.screen, self.game.camera.pos)
            if selector.index_int:
                reset_CharacterActiveObject(
                    self.dummy_list[selector.team - 1],
                    self.game,
                    selector.team,
                    self.game.dummy_input_device,
                    selector.menu[selector.selected_index].name,
                    (0, 0, 0),
                    1 if selector.team == 1 else -1,
                    0,
                    "Stand",
                )
            if selector.selected and selector.select_int == 1:
                get_state(self.dummy_list[selector.team - 1], {"Victory": 2})
            if selector.select_int == -1:
                get_state(self.dummy_list[selector.team - 1], {"Stand": 2})
        for dummy in self.dummy_list:
            dummy.update(self.game.camera_focus_point)
            dummy.fet = "grounded"
            dummy.pos = [-500, 140, 50] if dummy.team == 1 else [500, 140, 50]
            dummy.draw(self.game.screen, self.game.camera.pos)

        if not (None in [selected.selected_name for selected in self.menu_selectors]):
            self.selection_timer -= 1
            if self.selection_timer == 0:
                self.game.active = False
        else:
            self.selection_timer = 120

    def __dein__(self):
        self.game.selected_characters = [
            selected.selected_name for selected in self.menu_selectors
        ]
        self.game.selected_stage = ["Reencor/Training"]


class VersusScreen:
    def __init__(self, game, *args):
        self.game = game
        game.camera.pos = [0, 320, 400]
        self.selected_stage_objects = []
        self.selected_character_objects = []

        load_objects(game, self)

        self.slow_proportion = 0
        self.slow_timer = 0
        self.gameplay_update_timer = 0
        self.finish_round = False

    def __loop__(self):
        if self.finish_round and self.slow_timer < 120:
            if self.selected_character_objects[0].gauges["health"]:
                self.selected_character_objects[0].current_command.append("victorious")
            if self.selected_character_objects[1].gauges["health"]:
                self.selected_character_objects[1].current_command.append("victorious")
        if not self.gameplay_update_timer:
            self.game.gameplay()
        self.game.display()
        self.gameplay_update_timer = (
            self.gameplay_update_timer - 1
            if self.gameplay_update_timer
            else self.slow_proportion
        )
        self.slow_timer -= 1
        if self.slow_timer == 120:
            self.slow_proportion = 0
        if self.slow_timer == 1:
            self.game.active = False

        if not self.finish_round:
            for active_object in self.selected_character_objects:
                if active_object.gauges["health"] <= 0:
                    self.game.object_list += [
                        Message(
                            game=self.game,
                            pos=[-150, -150, 1],
                            scale=[6, 6],
                            string="KO",
                            time=60,
                            gradient_timer=60,
                            kill_on_time=True,
                            top=False,
                            shake=[20, 20, 60],
                        )
                    ]
                    for active_object in self.selected_character_objects:
                        active_object.inputdevice = self.game.dummy_input_device
                    self.slow_proportion, self.slow_timer, self.finish_round = (
                        1,
                        240,
                        True,
                    )
                    break

    def __dein__(self):
        self.game.screen_sequence += [VersusScreen]


class TrainingScreen:
    def __init__(self, game, *args):
        self.game = game
        game.camera.pos = [0, 320, 400]
        self.selected_stage_objects = []
        self.selected_character_objects = []
        self.game.show_inputs = True

        load_objects(game, self)

        self.selected_character_objects[0].gauges["super"] = 1100
        self.selected_character_objects[1].gauges["super"] = 1100
        self.guard_timer = 0

    def __loop__(self):
        if self.selected_character_objects[1].hitstun == 1:
            self.guard_timer = 50
            self.selected_character_objects[1].guard = weighted_choice(
                {"block": {"chance": 10}, "parry": {"chance": 1}}
            )
            for active_object in self.selected_character_objects:
                active_object.gauges["super"] = 1100

        self.guard_timer -= 1 if self.guard_timer else 0
        if self.guard_timer == 1:
            self.selected_character_objects[1].guard = ""
            self.selected_character_objects[1].gauges["health"] = 1100

        for active_object in self.selected_character_objects:
            if active_object.gauges["health"] <= 0:
                active_object.gauges["health"] = 1100

        self.game.gameplay()
        self.game.display()

    def __dein__(self):
        pass


class ComboTrialScreen:
    def __init__(self, game: object = object, trial_level: int = 0, *args):
        self.game = game
        game.camera.pos = [0, 320, 400]
        self.selected_stage_objects = []
        self.selected_character_objects = []
        self.game.show_inputs = True

        load_objects(game, self)

        game.input_device_list[0].team = 2

        self.trial_level = trial_level
        self.trial_move_list = self.selected_character_objects[0].dict["combo_trails"][
            trial_level
        ]
        self.trial_move_index = 0
        self.other_last_hitstun = 0
        self.trial_message_list = []
        self.finish_timer = 120
        self.finish_round = False

        self.selected_character_objects[0].gauges["super"] = 1100
        self.selected_character_objects[1].gauges["super"] = 1100
        if self.trial_move_list.get("start_pos", False):
            self.selected_character_objects[0].pos = self.trial_move_list["start_pos"][
                0
            ] + [0]
            self.selected_character_objects[1].pos = self.trial_move_list["start_pos"][
                1
            ] + [0]
            self.game.pos[0] = (
                self.trial_move_list["start_pos"][0][0]
                + self.trial_move_list["start_pos"][1][0]
            ) / 2

        self.guard_timer = 0

        for ind, move in enumerate(self.trial_move_list["sequence"]):
            self.trial_message_list.append(
                Message(
                    game=game,
                    pos=[-600, 160 - 40 * ind, 0],
                    string=move.get("comment", ""),
                    texture_string=[
                        {"image": "reencor/" + input, "size": (70, 70)}
                        for input in move["input"].split(",")
                    ],
                    background=(0,0,0,140),
                    time=20000,
                    gradient_timer=20000,
                    scale=(0.5, 0.5),
                )
            )

        self.game.object_list += self.trial_message_list

    def __loop__(self):
        self.other_last_hitstun = self.selected_character_objects[1].hitstun
        if self.finish_round:
            for active_object in self.selected_character_objects:
                active_object.current_command.append("victorious")

        else:
            move_match = False
            if self.trial_move_list["sequence"][self.trial_move_index].get("hit", True):
                if len(self.selected_character_objects[0].combo_list):
                    if (
                        self.selected_character_objects[0].combo_list[-1]
                        == self.trial_move_list["sequence"][self.trial_move_index][
                            "move"
                        ]
                    ):
                        self.selected_character_objects[0].combo_list = []
                        move_match = True
            else:
                if (
                    self.selected_character_objects[0].current_state
                    == self.trial_move_list["sequence"][self.trial_move_index]["move"]
                ):
                    move_match = True

            if move_match:
                self.trial_message_list[self.trial_move_index].color = (0, 0, 0, 255)
                self.trial_message_list[self.trial_move_index].pos[2] = -20
                object_display_shake(
                    self.trial_message_list[self.trial_move_index], [60, 0, 20, "self"]
                )
                self.trial_move_index += 1
                if self.trial_move_index == len(self.trial_move_list["sequence"]):
                    self.trial_level += 1
                    self.trial_move_index = 0
                    self.finish_round = True
                    self.game.object_list.append(
                        Message(
                            game=self.game,
                            pos=[
                                (
                                    -180
                                    if self.trial_level
                                    < len(
                                        self.selected_character_objects[0].dict[
                                            "combo_trails"
                                        ]
                                    )
                                    else -430
                                ),
                                0,
                                -1,
                            ],
                            string=(
                                " COMPLETE "
                                if self.trial_level
                                < len(
                                    self.selected_character_objects[0].dict[
                                        "combo_trails"
                                    ]
                                )
                                else " ALL TRIALS COMPLETE "
                            ),
                            background=(0, 0, 0, 126),
                            time=20000,
                            top=False,
                            shake=[20, 20, 10],
                        )
                    )

        if self.guard_timer and not self.selected_character_objects[1].hitstun and not self.selected_character_objects[1].hitstop:
            self.guard_timer -= 1 
            if not self.guard_timer:
                self.selected_character_objects[1].guard = ""
                self.selected_character_objects[1].gauges["health"] = 1100

        for active_object in self.selected_character_objects:
            if active_object.gauges["health"] <= 0:
                active_object.gauges["health"] = 1100

        self.game.gameplay()
        self.game.display()

        if self.other_last_hitstun and not self.selected_character_objects[1].hitstun:
            self.guard_timer = 50
            self.trial_move_index = 0
            self.selected_character_objects[0].combo_list = []
            self.selected_character_objects[1].guard = weighted_choice(
                {"block": {"chance": 10}, "parry": {"chance": 1}}
            )
            for active_object in self.selected_character_objects:
                active_object.gauges["super"] = 1100

            for message in self.trial_message_list:
                message.color = (255, 255, 255, 255)
                message.draw_shake = [0, 0, 0, 0, 0, 0]
                message.pos[2] = 0

        if self.finish_round:
            self.finish_timer -= 1
            if self.finish_timer == 0:
                self.game.active = False

    def __dein__(self):
        if self.trial_level == len(
            self.selected_character_objects[0].dict["combo_trails"]
        ):
            return
        self.game.screen_sequence += [ComboTrialScreen]
        self.game.screen_parameters = [self.trial_level]


class EditScreen:
    def __init__(self, game):
        self.game = game
        self.game.selected_characters = ["terry SVS", "ryu SF3"]
        self.game.selected_stage = ["grid stage"]
        self.game.camera_focus_point = (0, 600, -250)
        self.add_object = [
            BaseActiveObject(game, game.selected_stage[0]),
            BaseActiveObject(
                game,
                1,
                game.input_device_list[1],
                game.selected_characters[0],
                (0, 800),
                1,
                0,
            ),
            BaseActiveObject(
                game,
                2,
                game.input_device_list[1],
                game.selected_characters[1],
                (300, 800),
                -1,
                1,
            ),
            Combo_Counter(game, 1),
            Combo_Counter(game, 2),
            Gauge_Bar(game, 1, "health"),
            Gauge_Bar(game, 1, "super"),
            Gauge_Bar(game, 2, "health"),
            Gauge_Bar(game, 2, "super"),
        ]

        for ob in self.add_object:
            self.game.object_list.append(ob)
        for object in self.game.object_list:
            object.update(self.game.camera_focus_point)

        self.draw_boxes = True
        self.move_index, self.current_frame = 0, 0
        self.cursor = Menu_Cursor(self.game.object_list[2])

        box_types = {
            "hurtbox": self.cursor.change_box_type,
            "hitbox": self.cursor.change_box_type,
            "takebox": self.cursor.change_box_type,
            "grabox": self.cursor.change_box_type,
            "pushbox": self.cursor.change_box_type,
            "triggerbox": self.cursor.change_box_type,
            "boundingbox": self.cursor.change_box_type,
        }
        self.boxes_menu = [
            Menu_Item_String(
                type, (20, 20 + index * 40, 10), (1, 1), box_types[type], type
            )
            for index, type in enumerate(box_types)
        ]

        actions = {
            "New boxes": [self.cursor.new_boxes, None],
            "Save boxes": [self.cursor.save_boxes, None],
            "Character": [
                self.game.next_screen,
                [SinglePlayerCharacterSelectionScreen],
            ],
            "Mode": [self.game.next_screen, [ModeSelectionScreen]],
        }
        self.action_menu = [
            Menu_Item_String(
                type,
                (20, 20 + index * 40, 10),
                (1, 1),
                actions[type][0],
                actions[type][1],
            )
            for index, type in enumerate(actions)
        ]

        self.value_menu = [
            Menu_Item_String(type, (20, 20 + index * 40, 10), (1, 1))
            for index, type in enumerate(function_dict)
        ]

    def __loop__(self):

        for boxes in self.boxes_menu:
            boxes.update(self.game.camera_focus_point)
            boxes.draw(self.game.screen, self.game.camera.pos)

        for action in self.action_menu:
            action.update(self.game.camera_focus_point)
            action.draw(self.game.screen, self.game.camera.pos)

        for value in self.value_menu:
            value.update(self.game.camera_focus_point)
            value.draw(self.game.screen, self.game.camera.pos)

        if (
            self.game.input_device_list[0].current_input[0] == "2"
            and self.game.input_device_list[0].inter_press
        ):
            self.move_index = (
                self.move_index + 1
                if self.move_index
                < len(
                    list(self.game.object_dict[self.game.object_list[1].name]["states"])
                )
                - 1
                else 0
            )
            get_state(
                self.game.object_list[1],
                {
                    list(
                        self.game.object_dict[self.game.object_list[1].name]["states"]
                    )[self.move_index]: 1
                },
                1,
            )
            for object in self.game.object_list[1:]:
                object.update()
            self.current_frame = 0
        elif (
            self.game.input_device_list[0].current_input[0] == "8"
            and self.game.input_device_list[0].inter_press
        ):
            self.move_index = (
                len(
                    list(self.game.object_dict[self.game.object_list[1].name]["states"])
                )
                - 1
                if self.move_index < 1
                else self.move_index - 1
            )
            get_state(
                self.game.object_list[1],
                {
                    list(
                        self.game.object_dict[self.game.object_list[1].name]["states"]
                    )[self.move_index]: 1
                },
                1,
            )
            for object in self.game.object_list[1:]:
                object.update()
            self.current_frame = 0

        if (
            self.game.input_device_list[0].current_input[0] == "4"
            and self.game.input_device_list[0].inter_press
        ):
            self.current_frame = (
                self.current_frame + 1
                if self.current_frame
                < len(
                    self.game.object_dict[self.game.object_list[1].name]["states"][
                        self.game.object_list[1].current_state
                    ]["framedata"]
                )
                - 1
                else 0
            )
            self.game.object_list[1].frame = [self.current_frame, 0]
            for object in self.game.object_list[1:]:
                object.update()
        elif (
            self.game.input_device_list[0].current_input[0] == "6"
            and self.game.input_device_list[0].inter_press
        ):
            self.current_frame = (
                len(
                    self.game.object_dict[self.game.object_list[1].name]["states"][
                        self.game.object_list[1].current_state
                    ]["framedata"]
                )
                - 1
                if self.current_frame < 1
                else self.current_frame - 1
            )
            self.game.object_list[1].frame = [self.current_frame, 0]
            for object in self.game.object_list[1:]:
                object.update()

        (
            self.game.object_list[1].pos,
            self.game.object_list[1].speed[0],
            self.game.object_list[2].pos,
        ) = ([0, 800, 0], 0, [4000, 600, 0])

        draw_string(
            self.game.screen,
            "State: " + str(self.game.object_list[1].current_state),
            (-200, 380, 10),
            (1, 1),
            (0, 0, 0, 255),
        )
        draw_string(
            self.game.screen,
            "Substate: " + str(self.game.object_list[1].frame[0]),
            (-200, 400, 10),
            (1, 1),
            (0, 0, 0, 255),
        )
        draw_string(
            self.game.screen,
            "Sprite: "
            + str(
                self.game.object_dict[self.game.object_list[1].name]["states"][
                    self.game.object_list[1].current_state
                ]["framedata"][-self.game.object_list[1].frame[0] - 1].get(
                    "sprite", "NONE"
                )
            ),
            (-200, 420, 10),
            (1, 1),
            (0, 0, 0, 255),
        )

        for object in self.game.object_list:
            update_display_shake(object)
            object.draw(self.game.screen, self.game.camera.pos)
            if self.draw_boxes:
                draw_boxes(self.game, object)

    def __dein__(self):
        pass


class DebuggingScreen:
    def __init__(self, game):
        self.game = game
        game.camera.pos = [0, 320, 400]
        self.selected_stage_objects = []
        self.selected_character_objects = []
        self.game.show_boxes = True
        self.game.show_inputs = True

        load_objects(game, self)

        self.selected_character_objects[0].gauges["super"] = 1100
        self.selected_character_objects[1].gauges["super"] = 1100

    def __loop__(self):
        for active_object in self.selected_character_objects:
            if active_object.gauges["health"] <= 0:
                active_object.gauges["health"] = 1100
        self.game.gameplay()
        self.game.display()

    def __dein__(self):
        pass
