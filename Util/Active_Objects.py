from pygame import mixer
from Util.Common_functions import (
    RoundSign,
    get_command,
    get_state,
    next_frame,
    get_object_per_team,
    object_kill,
)
from Util.Input_device import InputDevice, dummy_input


class BaseActiveObject:
    def __init__(
        self,
        game: object = object,
        dict: dict = {},
        pos: list = [0, 0, 0],
        face: int = 1,
        inicial_state: str = False,
        palette: int = 0,
        inputdevice: InputDevice = dummy_input,
        team: int = 1,
        parent: object = None
    ):
        (
            self.game,
            self.type,
            self.dict,
            self.team,
            self.inputdevice,
            self.pos,
            self.face,
            self.palette,
            self.parent
        ) = (
            game,
            dict.get("type", "character").casefold(),
            dict,
            team,
            inputdevice,
            ([pos[0], pos[1], 0] if len(pos) == 2 else pos),
            face,
            palette,
            parent
        )
        (
            self.hurt_coll_hit,
            self.hit_coll_hurt,
            self.trigger_coll_hurt,
            self.take_coll_grab,
        ) = ([], [], [], [])
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
        self.current_command, self.command_index_timer = [5], {
            move: [[0, 0] for ind in self.dict["states"][move].get("command", ())]
            for move in self.dict["states"]
            if self.dict["states"][move].get("command", False)
        }
        self.mass, self.scale, self.time_kill, self.gauges, self.boxes = (
            self.dict["mass"],
            self.dict["scale"],
            self.dict["timekill"],
            {
                gauge: self.dict["gauges"][gauge]["inicial"]
                for gauge in self.dict["gauges"]
            },
            self.dict["boxes"],
        )
        (
            self.frame,
            self.repeat,
            self.ignore_stop,
            self.hold_on_stun,
            self.hitstun,
            self.hitstop,
        ) = ([0, 0], 0, False, False, 0, 0)
        (
            self.speed,
            self.acceleration,
            self.con_speed,
            self.air_time,
            self.air_max_height,
        ) = ([0, 0], [0, 0], [0, 0], 0, 0)
        (
            self.fet,
            self.grabed,
            self.cancel,
            self.kara,
            self.current_state,
            self.buffer_state,
            self.wallbounce,
        ) = ("grounded", None, [0], 0, "Stand", {}, False)
        (
            self.combo,
            self.parry,
            self.guard,
            self.juggle,
            self.damage_scaling,
            self.last_damage,
        ) = (0, ["6", 0], "", 100, [100, 100], [0, 0])
        self.move_raw_input = {
            move: []
            for move in self.dict["states"]
            if self.dict["states"][move].get("command", False)
        }
        self.self_main_object, self.other_main_object, self.influence_object, inputdevice.active_object, self.combo_list = (
            None,
            None,
            None,
            self,
            []
        )
        
        get_state(self, {inicial_state: 2}, 1), next_frame(
            self, self.dict["states"][self.current_state]["framedata"][0]
        )

    def update(self, *args):

        if self.self_main_object == None:
            self.self_main_object = get_object_per_team(
                self.game.object_list, self.team, False
            )
        if self.other_main_object == None:
            self.other_main_object = get_object_per_team(
                self.game.object_list, self.team
            )

        if (
            (
                "3" in self.inputdevice.current_input or "6" in self.inputdevice.current_input
            )
            and self.inputdevice.inter_press
            and self.parry[1] == 0
        ):
            self.parry = [self.inputdevice.current_input[0], 24]
        self.parry[1] = self.parry[1] - 1 if self.parry[1] else 0
        for gauge in self.gauges:
            if self.gauges[gauge] < 0:
                self.gauges[gauge] = 0
            if self.gauges[gauge] > self.dict["gauges"][gauge]["max"]:
                self.gauges[gauge] = self.dict["gauges"][gauge]["max"]
        for move in self.command_index_timer:
            for ind in range(len(self.command_index_timer[move])):
                self.command_index_timer[move][ind] = [
                    (
                        self.command_index_timer[move][ind][0]
                        if self.command_index_timer[move][ind][1]
                        else 0
                    ),
                    (
                        self.command_index_timer[move][ind][1] - 1
                        if self.command_index_timer[move][ind][1]
                        else 0
                    ),
                ]
        if (not self.hitstop) and (self.grabed == None):
            if self.hitstun:
                self.hitstun -= 1
            if self.other_main_object!= None:
                if (
                    (
                        set(self.cancel).intersection(["neutral", "turn", "kara"])
                        or self.frame == [0, 0]
                    )
                    and self.fet == "grounded"
                    and self.face != RoundSign(self.other_main_object.pos[0] - self.pos[0])
                    and abs(self.other_main_object.pos[0] - self.pos[0]) > 32
                ):
                    self.face, self.current_command, self.inputdevice.inter_press = (
                        RoundSign(self.other_main_object.pos[0] - self.pos[0]),
                        ["turn"] + self.current_command,
                        1,
                    )
                
            self.speed = [
                self.speed[0] + self.acceleration[0] * self.face,
                self.speed[1] + self.acceleration[1],
            ]
            self.pos = [
                self.pos[0] + self.speed[0],
                self.pos[1] + self.speed[1],
                self.pos[2],
            ]
            if self.fet == "airborne":
                self.speed[1] = self.speed[1] + self.dict["gravity"]

            self.buffer_state = {
                timer: self.buffer_state[timer] - 1
                for timer in self.buffer_state
                if self.buffer_state[timer] > 0
            }
        if self.inputdevice.inter_press or (self.frame[0] <= 0 and self.frame[1] <= 0) or (not set(self.cancel).intersection([None]) or self.kara):
            self.current_command += list(self.inputdevice.current_input)
            get_command(self, self.current_command)
        if (
            (self.inputdevice.inter_press or self.buffer_state)
            and (not set(self.cancel).intersection([None]) or self.kara)
            and (self.hitstop == 0 or self.hitstop and self.ignore_stop)
        ) or (self.frame[0] <= 0 and self.frame[1] <= 0):
            get_state(self, self.buffer_state)
        self.frame[1] -= 1 * (
            ((self.hitstop and self.ignore_stop) or (not self.hitstop))
            and ((self.hold_on_stun and not self.hitstun) or (not self.hold_on_stun))
        )
        if self.frame[1] <= 0:
            next_frame(
                self,
                self.dict["states"][self.current_state]["framedata"][-self.frame[0]],
            )
        if self.con_speed[0] or self.con_speed[1]:
            self.speed = [
                self.speed[0] + self.con_speed[0],
                self.speed[1] + self.con_speed[1],
            ]
        if self.hitstop:
            self.hitstop = self.hitstop - 1
        if self.kara:
            self.kara -= 1
        self.current_command = []
        if type(self.time_kill) != bool:
            self.time_kill -= 1
            if self.time_kill == 0:
                object_kill(self)

    def draw(self, screen, pos, *args):
        for texture in [{"image": self.image}] + self.draw_textures:
            screen.draw_texture(
                self.game.image_dict[texture["image"]][0],
                (
                    (self.draw_shake[0] + self.pos[0] - ((texture.get("image_offset", self.image_offset)[0]) * (1 if self.face < 0 else -1)) - (0 if self.face < 0 else texture.get("image_size", self.image_size)[0] * self.scale))if type(texture.get("image_offset", self.image_offset)[0])==int else (pos[0] + int(texture.get("image_offset", self.image_offset)[0])),
                    (self.draw_shake[1] + self.pos[1] + texture.get("image_offset", self.image_offset)[1])if type(texture.get("image_offset", self.image_offset)[1])==int else (pos[1] + int(texture.get("image_offset", self.image_offset)[1])),
                    (self.pos[2] + texture.get("image_offset", self.image_offset)[2])if type(texture.get("image_offset", self.image_offset)[2])==int else (pos[2] + int(texture.get("image_offset", self.image_offset)[2])),
                ),
                texture.get("image_size", self.image_size),
                ((self.face > 0) ^ texture.get("image_mirror", (False,False))[0], texture.get("image_mirror", (False,False))[1]),
                texture.get("image_tint", self.image_tint),
                texture.get("image_angle", self.image_angle),
                texture.get("image_repeat", self.image_repeat),
                texture.get("image_glow", self.image_glow),
                texture.get("type", self.type) == "character",
            )

def reset_CharacterActiveObject(
        self: object = object,
        game: object = object,
        dict: dict = {},
        pos: list = [0, 0, 0],
        face: int = 1,
        inicial_state: str = False,
        palette: int = 0,
        inputdevice: InputDevice = dummy_input,
        team: int = 1,
        parent: object = None
    ):
        (
            self.game,
            self.type,
            self.dict,
            self.team,
            self.inputdevice,
            self.pos,
            self.face,
            self.palette,
            self.parent
        ) = (
            game,
            dict.get("type", "character").casefold(),
            dict,
            team,
            inputdevice,
            ([pos[0], pos[1], 0] if len(pos) == 2 else pos),
            face,
            palette,
            parent
        )
        (
            self.hurt_coll_hit,
            self.hit_coll_hurt,
            self.trigger_coll_hurt,
            self.take_coll_grab,
        ) = ([], [], [], [])
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
        self.current_command, self.command_index_timer = [5], {
            move: [[0, 0] for ind in self.dict["states"][move].get("command", ())]
            for move in self.dict["states"]
            if self.dict["states"][move].get("command", False)
        }
        self.mass, self.scale, self.time_kill, self.gauges, self.boxes = (
            self.dict["mass"],
            self.dict["scale"],
            self.dict["timekill"],
            {
                gauge: self.dict["gauges"][gauge]["inicial"]
                for gauge in self.dict["gauges"]
            },
            self.dict["boxes"],
        )
        (
            self.frame,
            self.repeat,
            self.ignore_stop,
            self.hold_on_stun,
            self.hitstun,
            self.hitstop,
        ) = ([0, 0], 0, False, False, 0, 0)
        (
            self.speed,
            self.acceleration,
            self.con_speed,
            self.air_time,
            self.air_max_height,
        ) = ([0, 0], [0, 0], [0, 0], 0, 0)
        (
            self.fet,
            self.grabed,
            self.cancel,
            self.kara,
            self.current_state,
            self.buffer_state,
            self.wallbounce,
        ) = ("grounded", None, [0], 0, "Stand", {}, False)
        (
            self.combo,
            self.parry,
            self.guard,
            self.juggle,
            self.damage_scaling,
            self.last_damage,
        ) = (0, ["6", 0], "", 100, [100, 100], [0, 0])
        self.move_raw_input = {
            move: []
            for move in self.dict["states"]
            if self.dict["states"][move].get("command", False)
        }
        self.self_main_object, self.other_main_object, self.influence_object = (
            None,
            None,
            None,
        )
        
        get_state(self, {inicial_state: 2}, 1), next_frame(
            self, self.dict["states"][self.current_state]["framedata"][0]
        )

