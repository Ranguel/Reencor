import os
import json
from pygame import mouse
from Util.OpenGL_Renderer import (
    get_string_size,
    get_texture_string_size,
    draw_string,
    draw_texture_as_string,
    Screen
)
from Util.Common_functions import (
    colors,
    gradient_color,
    nomatch,
    get_state,
    next_frame,
    object_display_shake,
    object_image,
    object_kill,
)
from Util.Box_Collitions import box_collide

current_dir = os.path.dirname(os.path.realpath(__file__))

color = [
    (255, 0, 0, 255),
    (0, 0, 255, 255),
    (0, 255, 0, 255),
    (255, 255, 0, 255),
    (255, 0, 255, 255),
    (0, 255, 255, 255),
    (255, 128, 0, 255),
    (128, 0, 255, 255),
    (0, 128, 255, 255),
    (128, 255, 0, 255),
    (255, 0, 128, 255),
    (0, 128, 128, 255),
]


class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            formatted_items = []
            for key, value in obj.items():
                if isinstance(value, dict) and key == "states":
                    formatted_states = ",\n    ".join(
                        f'"{k}": {json.dumps(v)}' for k, v in value.items()
                    )
                    formatted_value = "{\n    " + formatted_states + "\n}"
                elif isinstance(value, dict):
                    formatted_value = json.dumps(value, separators=(",", ": "))
                else:
                    formatted_value = json.dumps(value, separators=(",", ": "))
                formatted_items.append(f'"{key}": {formatted_value}')
            return "{\n  " + ",\n  ".join(formatted_items) + "\n}"
        return super().encode(obj)


class Menu_Item:
    def __init__(
        self,
        game: object,
        name: str = "dummy",
        image: str = "reencor/none",
        pos: list = [0, 0, 0],
        size: tuple = (100, 100),
        face: int = -1,
        func: callable = nomatch,
        param: any = None,
    ):
        (
            self.game,
            self.name,
            self.pos,
            self.size,
            self.face,
            self.func,
            self.param,
            self.timer,
        ) = (
            game,
            name,
            pos,
            size,
            face,
            func,
            param,
            0,
        )
        (
            self.image,
            self.image_offset,
            self.image_size,
            self.image_mirror,
            self.image_tint,
            self.image_angle,
            self.image_repeat,
            self.image_glow,
            self.draw_textures,
            self.draw_shake,
        ) = (
            "reencor/none",
            (0, 0, 0),
            size,
            (False, False),
            (255, 255, 255, 255),
            (0, 0, 0),
            False,
            0,
            [],
            [0, 0, 0, 0, 0, 0],
        )
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            (255, 255, 255, 255),
            (0, 0, 0),
            False,
            1,
        )
        self.type = "menu item"
        self.scale = 1
        self.frame = [0, 0]
        self.current_state = "Stand"
        self.timer = 0
        object_image(self, image)

    def selected(self):
        self.timer = 8

    def update(self, *args):
        if self.timer:
            self.timer -= 1

    def draw(self, screen: Screen, pos: tuple=(0,0,0), *args):
        for texture in [{"image": self.image}] + self.draw_textures:
            screen.draw_texture(
                self.game.image_dict[texture["image"]][0],
                (
                    (
                        (
                            self.draw_shake[0]
                            + self.pos[0]
                            - (
                                (texture.get("image_offset", self.image_offset)[0])
                                * (1 if self.face < 0 else -1)
                            )
                            - (
                                0
                                if self.face < 0
                                else texture.get("image_size", self.image_size)[0]
                                * self.scale
                            )
                        )
                        if type(texture.get("image_offset", self.image_offset)[0])
                        == int
                        else (
                            pos[0]
                            + int(texture.get("image_offset", self.image_offset)[0])
                        )
                    ),
                    (
                        (
                            self.draw_shake[1]
                            + self.pos[1]
                            + texture.get("image_offset", self.image_offset)[1]
                        )
                        if type(texture.get("image_offset", self.image_offset)[1])
                        == int
                        else (
                            pos[1]
                            + int(texture.get("image_offset", self.image_offset)[1])
                        )
                    ),
                    (
                        (
                            self.pos[2]
                            + texture.get("image_offset", self.image_offset)[2]
                        )
                        if type(texture.get("image_offset", self.image_offset)[2])
                        == int
                        else (
                            pos[2]
                            + int(texture.get("image_offset", self.image_offset)[2])
                        )
                    ),
                ),
                texture.get("image_size", self.image_size),
                (
                    (self.face > 0)
                    and not texture.get("image_mirror", (False, False))[0],
                    texture.get("image_mirror", (False, False))[1],
                ),
                texture.get("image_tint", self.image_tint),
                texture.get("image_angle", self.image_angle),
                texture.get("image_repeat", self.image_repeat),
                texture.get("image_glow", self.image_glow),
                True,
            )


class Menu_Item_String:
    def __init__(
        self,
        game: object,
        name: str = "",
        string: str = "",
        pos: list = (0, 0, 0),
        scale: list = (1, 1),
        func: callable = nomatch,
        param: any = None,
        alignment: str = "right",
        color: list = (255, 255, 255, 255),
        gradient_timer: int = 0,
    ):
        (
            self.game,
            self.name,
            self.pos,
            self.size,
            self.scale,
            self.func,
            self.param,
            self.timer,
        ) = (
            game,
            name,
            pos,
            get_string_size(game.image_dict, name, scale),
            scale,
            func,
            param,
            0,
        )
        (
            self.image,
            self.image_size,
            self.image_offset,
            self.image_mirror,
            self.draw_shake,
        ) = (None, (100, 100), [0, 0], [False, False], [0, 0, 0, 0, 0, 0])
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            (255, 255, 255, 255),
            (0, 0, 0),
            False,
            1,
        )
        self.alignment = alignment
        self.color = color
        self.gradient_timer = 0
        self.string = string

    def selected(self):
        self.timer = 8

    def update(self, *args):
        if self.timer:
            self.timer -= 1

    def draw(self, screen: Screen, pos: tuple=(0,0,0), *args):

        draw_string(
            self.game.image_dict,
            screen,
            self.string,
            (
                self.draw_shake[0] + pos[0] + self.pos[0],
                self.draw_shake[1] + pos[1] + self.pos[1],
                self.pos[2] - self.timer,
            ),
            self.scale,
            self.color,
            self.alignment,
        )


class Menu_Selector:
    def __init__(
        self,
        game: object = object,
        team: int = 1,
        inputdevice: object = object,
        menu: tuple = (Menu_Item),
        index: int = 0,
    ):
        (
            self.game,
            self.team,
            self.inputdevice,
            self.selected_index,
            self.last_index,
            self.timer,
            self.selected,
            self.selected_name,
            self.pos,
            self.size,
        ) = (game, team, inputdevice, index, 0, 0, 0, None, (0, 0), (100, 100))
        self.menu = menu
        self.color = color[index]
        (
            self.image,
            self.image_size,
            self.image_offset,
            self.image_mirror,
            self.draw_shake,
        ) = (None, (100, 100), [0, 0], [False, False], [0, 0, 0, 0, 0, 0])
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            (255, 255, 255, 255),
            (0, 0, 0),
            False,
            0,
        )
        self.scale = [1, 1]
        self.select_int = 0
        self.index_int = 1

    def on_selection(self, *args):
        self.menu[self.selected_index].selected(), self.menu[self.selected_index].func()
        self.selected, self.selected_name, self.select_int = (
            1,
            self.menu[self.selected_index].name,
            1,
        )

    def on_deselection(self, *args):
        self.selected, self.selected_name, self.select_int = 0, None, -1

    def change_index(self, best_option, *args):
        self.selected_index, self.timer, self.last_index, self.index_int = (
            best_option,
            6,
            self.selected_index,
            1,
        )

    def update(self, *args):
        self.select_int, self.index_int = 0, 0
        best_option, best_score, self.timer = None, float("inf"), self.timer - 1
        if self.timer < 0:
            self.timer, self.last_index = 30, self.selected_index
        if self.inputdevice.inter_press:
            if "p_b3" in self.inputdevice.current_input:
                self.on_selection()
            if "p_b2" in self.inputdevice.current_input:
                self.on_deselection()
            if self.selected == 0:
                if self.inputdevice.current_input[0] != "5":
                    for ind in range(len(self.menu)):
                        if ind == self.selected_index:
                            continue
                        dx, dy = (
                            self.menu[self.selected_index].pos[0]
                            + self.menu[self.selected_index].size[0] / 2
                        ) - (self.menu[ind].pos[0] + self.menu[ind].size[0] / 2), (
                            self.menu[ind].pos[1] + self.menu[ind].size[1] / 2
                        ) - (
                            self.menu[self.selected_index].pos[1]
                            + self.menu[self.selected_index].size[1] / 2
                        )
                        if (
                            (self.inputdevice.current_input[0] == "6" and dx >= 0)
                            or (self.inputdevice.current_input[0] == "4" and dx <= 0)
                            or (self.inputdevice.current_input[0] == "2" and dy >= 0)
                            or (self.inputdevice.current_input[0] == "8" and dy <= 0)
                        ):
                            continue
                        score = (
                            abs(dx)
                            * (
                                3
                                if self.inputdevice.current_input[0]
                                in ("1", "3", "4", "6", "7", "9")
                                else 1
                            )
                        ) + (
                            abs(dy)
                            * (
                                3
                                if self.inputdevice.current_input[0]
                                in ("1", "2", "3", "7", "8", "9")
                                else 1
                            )
                        )
                        if score < best_score:
                            best_score, best_option = score, ind
                    if best_option != None:
                        self.change_index(best_option)

    def draw(self, screen: Screen, pos: tuple=(0,0,0), *args):
        screen.draw_rect(
            (
                pos[0]
                + self.draw_shake[0]
                + self.menu[self.selected_index].pos[0]
                + (
                    self.menu[self.last_index].pos[0]
                    - self.menu[self.selected_index].pos[0]
                )
                / 6
                * self.timer,
                pos[1]
                + self.draw_shake[1]
                + self.menu[self.selected_index].pos[1]
                + (
                    self.menu[self.last_index].pos[1]
                    - self.menu[self.selected_index].pos[1]
                )
                / 6
                * self.timer,
                self.menu[self.selected_index].size[0],
                self.menu[self.selected_index].size[1],
            ),
            gradient_color(
                0 if self.selected else self.timer, 30, self.color, (255, 255, 255, 255)
            ),
            5,
            False,
            -self.menu[self.selected_index].timer if self.selected else 0,
        )


class Menu_Deck:
    def __init__(
        self,
        name: str = "",
        pos=(0, 0, 0),
        size=(200, 200),
        items: list = [Menu_Item],
        selectors: list = (Menu_Selector),
    ):
        self.name, self.pos, self.size, self.items, self.selectors = (
            name,
            pos,
            size,
            items,
            selectors,
        )
        self.top_bar = (pos[0], pos[1], size[0], size[1] * 0.1)
        (
            self.image,
            self.image_size,
            self.image_offset,
            self.image_mirror,
            self.draw_shake,
        ) = (None, (100, 100), [0, 0], [False, False], [0, 0, 0, 0, 0, 0])
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            (255, 255, 255, 255),
            (0, 0, 0),
            False,
            0,
        )
        self.scale = [1, 1]

    def show_window(self):
        0

    def hide_window(self):
        0

    def update(self, *args):
        for item in self.items:
            item.update(self.surface)

        for selector in self.selectors:
            selector.update(self.surface, self.items)

    def draw(self, screen: Screen, pos: tuple=(0,0,0), *args):
        for item in self.items:
            item.draw(screen, pos)

        for selector in self.selectors:
            selector.draw(screen, pos)


class Menu_Cursor:
    def __init__(self, game, player):
        (
            self.player,
            self.rect,
            self.current_input,
            self.last_input,
            self.inter_press,
            self.selected,
            self.over,
            self.timer,
        ) = (player, (0, 0, 20, 20), (0, 0), (0, 0), 0, None, None, 0)
        self.edge_list, self.edge_edit, self.box_list, self.box_type = (
            (
                (-20, -20, 10, 10),
                (-20, -20, 10, 10),
                (-20, -20, 10, 10),
                (-20, -20, 10, 10),
            ),
            [False, 0],
            [],
            "",
        )
        self.box_addition = False
        self.box_edit = False
        self.selected_box_type = "hurtbox"
        self.game = game

    def change_box_type(self, selected_box_type):
        self.selected_box_type = selected_box_type

    def new_boxes(self, *args):
        self.box_edit, self.box_list, self.box_addition = True, [], True

    def save_boxes(self, *args):
        new_json = dict(self.game.object_dict[self.player.name])
        if self.box_addition:
            new_json["states"][self.player.current_state]["framedata"][
                -self.player.frame[0] - 1
            ][self.box_type] = {"boxes": self.box_list}
        else:
            for index in range(
                self.player.frame[0],
                len(new_json["states"][self.player.current_state]["framedata"]),
            ):
                if (
                    new_json["states"][self.player.current_state]["framedata"][
                        -index
                    ].get(self.box_type, None)
                    != None
                ):
                    new_json["states"][self.player.current_state]["framedata"][-index][
                        self.box_type
                    ]["boxes"] = self.box_list
                    break

        with open(
            current_dir + "/objects/" + str(self.player.name) + ".json", "w"
        ) as outfile:
            outfile.write(CustomJSONEncoder().encode(new_json))

        self.game.object_dict[self.player.name] = new_json

        self.box_edit, self.box_list, self.box_addition = False, [], False

    def Box_specific(self, screen: Screen, boxes = any, type="hurtbox", *args):
        if self.edge_edit[0] == False:
            coll_any = 0
            for index, box in enumerate(boxes):
                if box_collide(
                    -self.game.pos[0]
                    + self.player.rect.centerx
                    + box[0] * self.player.face
                    - box[2] * (self.player.face < 0),
                    -self.game.pos[1] + self.player.rect.centery - box[3] - box[1],
                    box[2],
                    box[3],
                    self.rect[0],
                    self.rect[1],
                    self.rect[2],
                    self.rect[3],
                ):
                    self.over, coll_any = index, coll_any + 1
                    if self.inter_press and 1 in self.current_input:
                        if index == self.selected:
                            if not self.box_addition:
                                self.box_list = []
                            self.selected, self.edge_list, self.edge_edit = (
                                None,
                                (
                                    (-20, -20, 10, 10),
                                    (-20, -20, 10, 10),
                                    (-20, -20, 10, 10),
                                    (-20, -20, 10, 10),
                                ),
                                [False, 0],
                            )
                        else:
                            if not self.box_addition:
                                self.box_list = self.player.boxes[type]["boxes"]
                            self.box_edit = True
                            self.selected, self.edge_list, self.box_type = (
                                index,
                                [
                                    (
                                        -self.game.pos[0]
                                        + self.player.rect.centerx
                                        + box[0] * self.player.face
                                        - box[2] * (self.player.face < 0)
                                        - 10,
                                        -self.game.pos[1]
                                        + self.player.rect.centery
                                        - box[1]
                                        - 10,
                                        20,
                                        20,
                                    ),
                                    (
                                        -self.game.pos[0]
                                        + self.player.rect.centerx
                                        + box[0] * self.player.face
                                        - box[2] * (self.player.face < 0)
                                        + box[2]
                                        - 10,
                                        -self.game.pos[1]
                                        + self.player.rect.centery
                                        - box[1]
                                        - 10,
                                        20,
                                        20,
                                    ),
                                    (
                                        -self.game.pos[0]
                                        + self.player.rect.centerx
                                        + box[0] * self.player.face
                                        - box[2] * (self.player.face < 0)
                                        + box[2]
                                        - 10,
                                        -self.game.pos[1]
                                        + self.player.rect.centery
                                        - box[3]
                                        - box[1]
                                        - 10,
                                        20,
                                        20,
                                    ),
                                    (
                                        -self.game.pos[0]
                                        + self.player.rect.centerx
                                        + box[0] * self.player.face
                                        - box[2] * (self.player.face < 0)
                                        - 10,
                                        -self.game.pos[1]
                                        + self.player.rect.centery
                                        - box[3]
                                        - box[1]
                                        - 10,
                                        20,
                                        20,
                                    ),
                                ],
                                type,
                            )
                        break
            if coll_any == 0:
                self.over = None
                if self.inter_press and self.current_input[0]:
                    if not self.box_edit:
                        self.box_list, self.box_addition = [], False
                    self.selected, self.edge_list, self.edge_edit = (
                        None,
                        (
                            (-20, -20, 10, 10),
                            (-20, -20, 10, 10),
                            (-20, -20, 10, 10),
                            (-20, -20, 10, 10),
                        ),
                        [False, 0],
                    )
                if self.inter_press and self.current_input[2]:
                    self.box_edit, self.box_type, self.box_addition, self.box_list = (
                        True,
                        type,
                        True,
                        self.box_list
                        + [
                            (
                                60,
                                60,
                                -self.player.rect.centerx
                                + self.rect.centerx
                                - self.game.pos[0],
                                self.player.rect.centery
                                - self.rect.centery
                                - self.game.pos[1],
                            )
                        ],
                    )

        for boxes_type in self.player.boxes:
            if boxes_type != type:
                for box in self.player.boxes[boxes_type].get("boxes", []):
                    screen.draw_rect(
                        gradient_color(5, 10, colors[boxes_type], (0, 0, 0)),
                        (
                            -self.game.pos[0]
                            + self.player.rect.centerx
                            + box[0] * self.player.face
                            - box[2] * (self.player.face < 0),
                            -self.game.pos[1]
                            + self.player.rect.centery
                            - box[3]
                            - box[1],
                            box[2],
                            box[3],
                        ),
                        3,
                    )
        for boxes_type in self.player.boxes:
            if boxes_type == type:
                for box in self.player.boxes[boxes_type].get("boxes", []):
                    screen.draw_rect(
                        colors[boxes_type],
                        (
                            -self.game.pos[0]
                            + self.player.rect.centerx
                            + box[0] * self.player.face
                            - box[2] * (self.player.face < 0),
                            -self.game.pos[1]
                            + self.player.rect.centery
                            - box[3]
                            - box[1],
                            box[2],
                            box[3],
                        ),
                        3,
                    )
        screen.draw_rect(
            (0, 0, 0),
            (
                -self.game.pos[0] + self.player.rect.centerx - 16,
                -self.game.pos[1] + self.player.rect.centery,
            ),
            (
                -self.game.pos[0] + self.player.rect.centerx + 16,
                -self.game.pos[1] + self.player.rect.centery,
            ),
            3,
        )
        screen.draw_rect(
            (0, 0, 0),
            (
                -self.game.pos[0] + self.player.rect.centerx,
                -self.game.pos[1] + self.player.rect.centery - 16,
            ),
            (
                -self.game.pos[0] + self.player.rect.centerx,
                -self.game.pos[1] + self.player.rect.centery + 16,
            ),
            3,
        )

        if self.over != None and self.selected == None:
            screen.draw_rect(
                gradient_color(self.timer, 30, (120, 120, 255), (255, 255, 255)),
                (
                    -self.game.pos[0]
                    + self.player.rect.centerx
                    + boxes[self.over][0] * self.player.face
                    - boxes[self.over][2] * (self.player.face < 0),
                    -self.game.pos[1]
                    + self.player.rect.centery
                    - boxes[self.over][3]
                    - boxes[self.over][1],
                    boxes[self.over][2],
                    boxes[self.over][3],
                ),
                4,
            )

    def menu_specific(self, menus, *args):
        for menu in menus:
            for item in menu.items:
                if (
                    box_collide(
                        menu.rect[0] + item.rect[0],
                        menu.rect[1] + item.rect[1],
                        item.rect[2],
                        item.rect[3],
                        self.rect[0],
                        self.rect[1],
                        self.rect[2],
                        self.rect[3],
                    )
                    and self.inter_press
                    and self.current_input[0]
                ):
                    item.selected()
                    item.func(item.param)
                    return

    def update(self, menus: list = (Menu_Deck), *args):
        self.current_input, self.rect.center, self.timer = (
            mouse.get_pressed(),
            mouse.get_pos(),
            0 if self.timer > 30 else self.timer + 1,
        )
        self.inter_press = 1 if self.current_input != self.last_input else 0

        self.menu_specific(menus)

        if self.selected != None:
            for index, rect in enumerate(self.edge_list):
                if box_collide(
                    rect[0],
                    rect[1],
                    rect[2],
                    rect[3],
                    self.rect[0],
                    self.rect[1],
                    self.rect[2],
                    self.rect[3],
                ):
                    if self.inter_press and self.current_input[2]:
                        self.box_list.pop(self.selected)
                        self.selected, self.edge_list, self.edge_edit = (
                            None,
                            (
                                (-20, -20, 10, 10),
                                (-20, -20, 10, 10),
                                (-20, -20, 10, 10),
                                (-20, -20, 10, 10),
                            ),
                            [False, 0],
                        )
                        break
                    if self.inter_press and self.current_input[0]:
                        self.edge_edit = [True, index]
                        break
            if not self.current_input[0]:
                self.edge_edit = [False, 0]
            if self.edge_edit[0]:
                self.edge_list[self.edge_edit[1]].center = self.rect.center
                if self.edge_edit[1] == 0:
                    self.edge_list[3].centerx, self.edge_list[1].centery = (
                        self.edge_list[self.edge_edit[1]].centerx,
                        self.edge_list[self.edge_edit[1]].centery,
                    )
                elif self.edge_edit[1] == 1:
                    self.edge_list[2].centerx, self.edge_list[0].centery = (
                        self.edge_list[self.edge_edit[1]].centerx,
                        self.edge_list[self.edge_edit[1]].centery,
                    )
                elif self.edge_edit[1] == 2:
                    self.edge_list[1].centerx, self.edge_list[3].centery = (
                        self.edge_list[self.edge_edit[1]].centerx,
                        self.edge_list[self.edge_edit[1]].centery,
                    )
                else:
                    self.edge_list[0].centerx, self.edge_list[2].centery = (
                        self.edge_list[self.edge_edit[1]].centerx,
                        self.edge_list[self.edge_edit[1]].centery,
                    )

                point_list_x, point_list_y = [
                    self.edge_list[0].centerx,
                    self.edge_list[1].centerx,
                    self.edge_list[2].centerx,
                    self.edge_list[3].centerx,
                ], [
                    self.edge_list[0].centery,
                    self.edge_list[1].centery,
                    self.edge_list[2].centery,
                    self.edge_list[3].centery,
                ]
                self.box_list[self.selected] = [
                    -self.player.rect.centerx + min(point_list_x) - self.game.pos[0],
                    self.player.rect.centery - max(point_list_y) - self.game.pos[1],
                    abs(max(point_list_x) - min(point_list_x)),
                    abs(max(point_list_y) - min(point_list_y)),
                ]

    def draw(self, screen: Screen):

        if self.box_edit:
            self.Box_specific(screen, self.box_list, self.selected_box_type)
        else:
            self.Box_specific(
                screen,
                self.player.boxes[self.selected_box_type].get("boxes", []),
                self.selected_box_type,
            )
        self.last_input = self.current_input

        if self.selected != None:
            screen.draw_rect(
                screen,
                (0, 0, 0),
                (self.edge_list[0].centerx, self.edge_list[0].centery),
                (self.edge_list[1].centerx, self.edge_list[1].centery),
                3,
            ), screen.draw_rect(
                (0, 0, 0),
                (self.edge_list[1].centerx, self.edge_list[1].centery),
                (self.edge_list[2].centerx, self.edge_list[2].centery),
                3,
            ), screen.draw_rect(
                (0, 0, 0),
                (self.edge_list[2].centerx, self.edge_list[2].centery),
                (self.edge_list[3].centerx, self.edge_list[3].centery),
                3,
            ), screen.draw_rect(
                (0, 0, 0),
                (self.edge_list[3].centerx, self.edge_list[3].centery),
                (self.edge_list[0].centerx, self.edge_list[0].centery),
                3,
            )
        for rect in self.edge_list:
            screen.draw_rect(screen, (255, 255, 255), rect)
        screen.draw_rect(
            screen,
            (20, 20, 20),
            0,
            (
                (self.rect.centerx + 8, self.rect.centery + 20),
                self.rect.center,
                (self.rect.centerx + 20, self.rect.centery + 8),
            ),
            8,
        )


class Combo_Counter:
    def __init__(self, game: object, parent: object):
        self.game, self.parent = game, parent
        self.image, self.image_size = None, (1000, 200)
        self.scale = [0.6, 0.6]
        self.pos, self.timer, self.gradient_timer = (40, 250, 0), 0, 0
        self.combo = 0
        self.draw_shake = [0, 0, 0, 0, 0, 0]

    def update(self, *args):
        if self.parent.combo != self.combo:
            self.combo, self.timer, self.gradient_timer = (
                self.parent.combo,
                (150) * (self.parent.combo > 1),
                (90) * (self.parent.combo > 1),
            )
        self.timer = self.timer - 1 if self.timer else 0
        self.gradient_timer = self.gradient_timer - 1 if self.gradient_timer else 6

    def draw(self, screen: Screen, pos: tuple=(0,0,0), *args):
        if self.timer:
            draw_string(
                self.game.image_dict,
                screen,
                "COMBO " + str(self.combo),
                (
                    self.draw_shake[0]
                    + (
                        pos[0] - ((screen.size[0] * 0.5) * abs(pos[2] / 400)) + 40
                        if self.parent.team == 1
                        else pos[0] + ((screen.size[0] * 0.5) * abs(pos[2] / 400)) - 40
                    ),
                    self.draw_shake[1]
                    + pos[1]
                    + ((screen.size[1] * 0.3) * abs(pos[2] / 400)),
                    self.pos[2] + self.draw_shake[1],
                ),
                self.scale,
                gradient_color(
                    self.gradient_timer, 6, (0, 0, 0, 0), (255, 255, 255, 255)
                ),
                "right" if self.parent.team == 1 else "left",
            )


class Gauge_Bar:
    def __init__(
        self,
        game: object,
        dict: dict = {},
        pos: list = [0, 0, 0],
        face: int = 1,
        inicial_state: str = False,
        palette: int = 0,
        parent: object = None,
    ):
        (
            self.game,
            self.type,
            self.dict,
            self.pos,
            self.face,
            self.palette,
            self.parent,
        ) = (
            game,
            dict.get("type", "bar").casefold(),
            dict,
            ([pos[0], pos[1], 0] if len(pos) == 2 else pos),
            parent.face,
            palette,
            parent,
        )
        (
            self.image,
            self.image_offset,
            self.image_size,
            self.image_mirror,
            self.image_tint,
            self.image_angle,
            self.image_repeat,
            self.image_glow,
            self.draw_textures,
            self.draw_shake,
        ) = (
            "reencor/none",
            (0, 0, 0),
            (100, 100, 0),
            (False, False),
            (255, 255, 255, 255),
            (0, 0, 0),
            False,
            0,
            [],
            [0, 0, 0, 0, 0, 0],
        )
        self.scale = self.dict["scale"]
        self.frame = [0, 0]
        self.current_state = "Stand"
        self.timer = 0
        get_state(self, {inicial_state: 2}, 1), next_frame(
            self, self.dict["states"][self.current_state]["framedata"][0]
        )

    def update(self, *args):
        if self.timer:
            self.timer -= 1
        else:
            self.timer = self.dict["bar"].get("blink", 0)

    def draw(self, screen: Screen, pos: tuple=(0,0,0), *args):
        color_grad = (
            gradient_color(
                self.timer,
                self.dict["bar"].get("blink", 0),
                self.dict["bar"]["color"][0],
                self.dict["bar"]["color"][1],
            )
            if self.dict["bar"].get("blink", 0)
            else gradient_color(
                self.parent.gauges[self.dict["name"]],
                self.parent.dict["gauges"][self.dict["name"]]["max"],
                self.dict["bar"]["color"][0],
                self.dict["bar"]["color"][1],
            )
        )
        screen.draw_line(
            [
                pos[0]
                + (
                    self.dict["bar"]["start"][0]
                    - round(
                        (self.dict["bar"]["start"][0] - self.dict["bar"]["end"][0])
                        * (
                            (
                                (
                                    self.parent.gauges[self.dict["name"]]
                                    / self.parent.dict["gauges"][self.dict["name"]][
                                        "max"
                                    ]
                                )
                                * self.dict["bar"]["level"]
                            )
                            % 1
                            + int(
                                self.parent.gauges[self.dict["name"]]
                                >= self.parent.dict["gauges"][self.dict["name"]]["max"]
                            )
                        )
                    )
                )
                * (1 if self.parent.team == 1 else -1),
                pos[1] + self.dict["bar"]["start"][1],
            ],
            [
                pos[0]
                + self.dict["bar"]["start"][0] * (1 if self.parent.team == 1 else -1),
                pos[1] + self.dict["bar"]["start"][1],
            ],
            color_grad,
            self.dict["bar"]["thickness"],
        )

        if self.dict["bar"].get("level_indicator", False):
            draw_string(
                self.game.image_dict,
                screen,
                str(
                    int(
                        (
                            self.parent.gauges[self.dict["name"]]
                            / self.parent.dict["gauges"][self.dict["name"]]["max"]
                        )
                        * self.dict["bar"]["level"]
                    )
                ),
                (
                    (
                        self.draw_shake[0]
                        + pos[0]
                        + self.dict["bar"]["level_indicator"][0]
                        * (1 if self.parent.team == 1 else -1),
                        self.draw_shake[1]
                        + pos[1]
                        + self.dict["bar"]["level_indicator"][1],
                        -2,
                    )
                ),
                (1.5, 1.5),
                (0, 0, 0, 0),
                "right" if self.parent.team == 1 else "left",
            )

        for texture in (
            [
                {
                    "image": self.parent.dict["portrait"],
                    "image_offset": self.dict["object_portrait"]["pos"],
                    "image_size": self.dict["object_portrait"]["size"],
                    "image_center": True,
                }
            ]
            if self.dict.get("object_portrait", False)
            else []
        ) + self.draw_textures:
            screen.draw_texture(
                self.game.image_dict[texture["image"]][0],
                (
                    (
                        (
                            self.draw_shake[0]
                            + self.pos[0]
                            - (
                                (texture.get("image_offset", self.image_offset)[0])
                                * (1 if self.face < 0 else -1)
                            )
                            - (
                                0
                                if self.face < 0
                                else texture.get("image_size", self.image_size)[0]
                                * self.scale
                            )
                        )
                        if type(texture.get("image_offset", self.image_offset)[0])
                        == int
                        else (
                            pos[0]
                            + int(texture.get("image_offset", self.image_offset)[0])
                            * self.face
                        )
                    ),
                    (
                        (
                            self.draw_shake[1]
                            + self.pos[1]
                            + texture.get("image_offset", self.image_offset)[1]
                        )
                        if type(texture.get("image_offset", self.image_offset)[1])
                        == int
                        else (
                            pos[1]
                            + int(texture.get("image_offset", self.image_offset)[1])
                        )
                    ),
                    (
                        (
                            self.pos[2]
                            + texture.get("image_offset", self.image_offset)[2]
                        )
                        if type(texture.get("image_offset", self.image_offset)[2])
                        == int
                        else (
                            pos[2]
                            + int(texture.get("image_offset", self.image_offset)[2])
                        )
                    ),
                ),
                texture.get("image_size", self.image_size),
                (
                    (self.face > 0)
                    and not texture.get("image_mirror", (False, False))[0],
                    texture.get("image_mirror", (False, False))[1],
                ),
                texture.get("image_tint", (255, 255, 255, 255)),
                texture.get("image_angle", (0, 0, 0)),
                texture.get("image_repeat", False),
                texture.get("image_glow", 0),
                True,
                texture.get("image_center", False),
            )


class Message:
    def __init__(
        self,
        game: object,
        pos: list = [0, 0, 0],
        scale: tuple = (1, 1),
        string: str = "",
        texture_string: list = [],
        background: tuple = (0, 0, 0, 0),
        time: int = 60,
        color: tuple = (255, 255, 255, 255),
        gradient_timer: int = 0,
        kill_on_time: bool = False,
        top: bool = True,
        shake: list = [0, 0, 0],
        allign: str = "right",
    ):
        (
            self.game,
            self.pos,
            self.scale,
            self.string,
            self.texture_string,
            self.background,
            self.timer,
            self.color,
            self.gradient_timer,
            self.kill_on_time,
            self.top,
            self.draw_shake,
            self.allign,
        ) = (
            game,
            pos,
            scale,
            string,
            texture_string,
            background,
            time,
            color,
            gradient_timer,
            kill_on_time,
            top,
            [0, 0, 0, 0, 0, 0],
            allign,
        )
        self.string_size = get_string_size(game.image_dict, string, scale)
        self.texture_string_size = get_texture_string_size(
            game.image_dict, texture_string, scale
        )
        self.size = self.string_size[0] + self.texture_string_size[0], max(
            self.string_size[1], self.texture_string_size[1]
        )
        object_display_shake(self, shake + ["self"])

    def update(self, *args):
        self.timer = self.timer - 1 if self.timer else 0
        self.gradient_timer = self.gradient_timer - 1 if self.gradient_timer else 6
        if self.kill_on_time and self.timer == 0:
            object_kill(self)

    def draw(self, screen: Screen, pos: tuple=(0,0,0), *args):
        if self.background != (0, 0, 0, 0):
            screen.draw_rect(
                rect=(
                    self.draw_shake[0] + pos[0] + self.pos[0] - (self.size[0] if self.allign == "left" else 0),
                    self.draw_shake[1] + pos[1] + self.pos[1],
                    self.size[0],
                    self.size[1],
                ),
                color=self.background,
                border_thickness=0,
                z_offset=self.pos[2]
            )

        draw_string(
            self.game.image_dict,
            screen,
            str(self.string),
            (
                self.draw_shake[0] + pos[0] + self.pos[0] - (self.texture_string_size[0] if self.allign == "left" else 0),
                self.draw_shake[1] + pos[1] + self.pos[1],
                self.pos[2],
            ),
            self.scale,
            self.color,#gradient_color(self.gradient_timer, 6, (0, 0, 0, 0), self.color)
            self.allign,
            self.top,
        )

        draw_texture_as_string(
            self.game.image_dict,
            screen,
            self.texture_string,
            (
                self.draw_shake[0] + pos[0] + self.pos[0] + (self.string_size[0] if self.allign == "right" else 0),
                self.draw_shake[1] + pos[1] + self.pos[1],
                self.pos[2],
            ),
            self.scale,
            self.color,#gradient_color(self.gradient_timer, 6, (0, 0, 0, 0), self.color)
            self.allign,
            self.top,
        )
