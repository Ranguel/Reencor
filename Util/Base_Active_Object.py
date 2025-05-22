import math, random
from Util.Input_device import InputDevice


class BaseActiveObject:
    def __init__(
        self,
        game=object,
        type: str = "character",
        dict: dict = {},
        team: int = 1,
        inputdevice=InputDevice,
        pos: list = (280, 200, 0),
        face: int = 1,
        palette: int = 0,
        inicial_state: str = False,
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
        ) = (
            game,
            type,
            dict,
            team,
            inputdevice,
            ([pos[0], pos[1], 0] if len(pos) == 2 else pos),
            face,
            palette,
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
            self.draw_shake,
        ) = (
            "reencor/none",
            [0, 0],
            (100, 100),
            [False, False],
            (255, 255, 255, 255),
            (0, 0, 0),
            False,
            0,
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
        if inicial_state:
            self.get_state({inicial_state: 2}, 1), self.next_frame(
                self.dict["states"][self.current_state]["framedata"][0]
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
                (self.inputdevice.current_input[0] in ["1", "3"] and self.face > 0)
                or (self.inputdevice.current_input[0] in ["4", "6"] and self.face < 0)
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
                self.pos[1] - self.speed[1],
                self.pos[2],
            ]
            if self.fet == "airborne":
                self.speed[1] = self.speed[1] + self.dict["gravity"]
            if self.hitstun == 0:
                self.other_main_object.damage_scaling = [100, 100]
            self.buffer_state = {
                timer: self.buffer_state[timer] - 1
                for timer in self.buffer_state
                if self.buffer_state[timer] > 0
            }
        if self.inputdevice.inter_press or (self.frame[0] <= 0 and self.frame[1] <= 0):
            self.current_command += list(self.inputdevice.current_input)
            self.get_command(self.current_command)
        if (
            (self.inputdevice.inter_press or self.buffer_state)
            and (not set(self.cancel).intersection([None]) or self.kara)
            and (self.hitstop == 0 or self.hitstop and self.ignore_stop)
        ) or (self.frame[0] <= 0 and self.frame[1] <= 0):
            self.get_state(self.buffer_state)
        self.frame[1] -= 1 * (
            ((self.hitstop != 0 and self.ignore_stop) or (not self.hitstop))
            and ((self.hold_on_stun and self.hitstun == 0) or (not self.hold_on_stun))
        )
        if self.frame[1] <= 0:
            self.next_frame(
                self.dict["states"][self.current_state]["framedata"][-self.frame[0]]
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
                self.object_kill()

    def draw(self, screen, *args):
        screen.draw_texture(
            self.image,
            (
                self.draw_shake[0]
                + self.pos[0]
                - ((self.image_offset[0]) * (1 if self.face < 0 else -1))
                - (0 if self.face < 0 else self.image_size[0] * self.scale),
                self.draw_shake[1] + self.pos[1] - (-self.image_offset[1]),
            ),
            self.image_size,
            ((self.face > 0) and not self.image_mirror[0], self.image_mirror[1]),
            self.image_tint,
            self.image_angle,
            self.image_repeat,
            self.image_glow,
        )
