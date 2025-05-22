import random
import math


colors = {
    "hurtbox": (20, 20, 255, 255),
    "hitbox": (255, 20, 20, 255),
    "takebox": (20, 255, 255, 255),
    "grabbox": (20, 255, 20, 255),
    "pushbox": (255, 0, 255, 255),
    "triggerbox": (255, 128, 0, 255),
    "boundingbox": (255, 255, 255, 255),
}

default_substate = {"dur": 1}

default_hitbox = {
    "damage": (0, 0),
    "gain": (0, 0),
    "stamina": (0, 0),
    "hitstun": (0, 0),
    "hitstop": 10,
    "juggle": 1,
    "knockback": {"grounded": [0, 0]},
    "hittype": ["medium", "middle"],
}

attack_type_value = {
    "parry": {"scaling": 10, "min_scaling": 0},
    "block": {"scaling": 10, "min_scaling": 10},
    "critical": {"scaling": 10, "min_scaling": 40},
    "super": {"scaling": 10, "min_scaling": 36},
    "special": {"scaling": 10, "min_scaling": 16},
    "heavy": {"scaling": 10, "min_scaling": 14},
    "medium": {"scaling": 9, "min_scaling": 12},
    "light": {"scaling": 8, "min_scaling": 10},
    "no_match": {"scaling": 8, "min_scaling": 40},
}

dummy_json = {
    "type": "projectile",
    "palette": [],
    "scale": [1, 1],
    "gravity": 0,
    "mass": 1,
    "music": "",
    "terminal_velocity": 1,
    "gauges": {},
    "boxes": {
        "hurtbox": {"boxes": []},
        "hitbox": {"boxes": [], "hitset": 1},
        "takebox": {"boxes": []},
        "grabbox": {"boxes": []},
        "pushbox": {"boxes": []},
        "triggerbox": {"boxes": []},
        "boundingbox": {"boxes": [[-75, 0, 150, 310]], "grounded_friction": 0.7},
    },
    "offset": [0, 0],
    "timekill": False,
    "trials": [],
    "states": {},
}


def nomatch(*args):
    pass


def gradient_color(value, max_value, color1, color2):
    if len(color1) == 3:
        color1 += [255]
    if len(color2) == 3:
        color2 += [255]
    if max_value == 0:
        return (0, 0, 0)
    value = max(0, min(value, max_value))
    t = value / max_value
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    try:
        a = int(color1[3] + (color2[3] - color1[3]) * t)
    except:
        print(max_value, color1, color2)
    return (r, g, b, a)


def normalizar(valor, min_valor, max_valor):
    return (valor - min_valor) / (max_valor - min_valor)


def reescale(values, escale):
    return [round(value * escale) for value in values]


def RoundSign(n):
    return int(1) if n > 0 else int(-1) if n < 0 else int(0)


def weighted_choice(options):
    values = list(options.keys())
    probabilities = [options[key]["chance"] for key in values]
    return random.choices(values, weights=probabilities, k=1)[0]


def get_object_per_team(
    object_list: list = [],
    team: int = 0,
    opposite: bool = True,
    type: str = "character",
):
    for self in object_list:
        if self.__class__.__name__ == "BaseActiveObject":
            if self.type == type.casefold() and (
                (self.team != team and opposite)
                or (self.team == team and opposite == False)
            ):
                return self


def get_object_per_class(object_list: list = [], type: str = "character"):
    for self in object_list:
        if self.__class__.__name__ == "BaseActiveObject":
            if self.type == type.casefold():
                return self


def update_display_shake(self):
    if self.draw_shake[2] == self.draw_shake[5]:
        self.draw_shake = [0, 0, 0, 0, 0, 0]
    if self.draw_shake[5]:
        factor = (
            math.sin((self.draw_shake[2] % 3) / 3 * math.pi * 2)
            * abs(self.draw_shake[5] - self.draw_shake[2])
            / self.draw_shake[5]
        )
        self.draw_shake = [
            self.draw_shake[3] * factor,
            self.draw_shake[4] * factor,
            self.draw_shake[2] + 1,
            self.draw_shake[3],
            self.draw_shake[4],
            self.draw_shake[5],
        ]


def normalize_vector(x, y, base=1):
    magnitude = math.sqrt(x**2 + y**2)
    if magnitude == 0:
        return [0, 1 * base]
    return [x / magnitude * base, y / magnitude * base]


mirror_pad = {
    "1": "3",
    "3": "1",
    "4": "6",
    "6": "4",
    "7": "9",
    "9": "7",
    "12": "32",
    "13": "31",
    "14": "36",
    "15": "35",
    "16": "34",
    "17": "39",
    "18": "38",
    "19": "37",
    "21": "23",
    "23": "21",
    "24": "26",
    "26": "24",
    "27": "29",
    "29": "27",
    "31": "13",
    "32": "12",
    "34": "16",
    "35": "15",
    "36": "14",
    "37": "19",
    "38": "18",
    "39": "17",
    "41": "63",
    "42": "62",
    "43": "61",
    "45": "65",
    "46": "64",
    "47": "69",
    "48": "68",
    "49": "67",
    "51": "53",
    "53": "51",
    "54": "56",
    "56": "54",
    "57": "59",
    "59": "57",
    "61": "43",
    "62": "42",
    "63": "41",
    "64": "46",
    "65": "45",
    "67": "49",
    "68": "48",
    "69": "47",
    "71": "93",
    "72": "92",
    "73": "91",
    "74": "96",
    "75": "95",
    "76": "94",
    "78": "98",
    "79": "97",
    "81": "83",
    "83": "81",
    "84": "86",
    "86": "84",
    "87": "89",
    "89": "87",
    "91": "73",
    "92": "72",
    "93": "71",
    "94": "76",
    "95": "75",
    "96": "74",
    "97": "79",
    "98": "78",
}


def get_command(self, state: list=[]):
    state = (
        [
            self.current_state,
            "crouch" if self.boxes["hurtbox"].get("crouch") != None else "stand",
        ]
        + ["defeated" if self.gauges.get("health", 1) <= 0 else "alive"]
        + state
    )
    for move in self.command_index_timer:
        for index in range(len(self.command_index_timer[move])):
            input_gate = self.dict["states"][move]["command"][index][self.command_index_timer[move][index][0]].split(",")
            intersection = 0
            for input in input_gate:
                if (
                    ("|" in input and set(input.split("|")) & set(state))
                    or ("!" in input and input.split("!")[1] not in state)
                    or (input in state)
                ):
                    intersection += 1
            if intersection >= len(input_gate):
                self.command_index_timer[move][index] = [
                    self.command_index_timer[move][index][0] + 1,
                    self.dict["states"][move].get("command_link_time", 14),
                ]
                if self.command_index_timer[move][index][0] >= len(
                    self.dict["states"][move]["command"][index]
                ):
                    self.buffer_state[move], self.command_index_timer[move][index] = (
                        self.dict["states"][move].get("buffer", 1),
                        [0, 0],
                    )

def get_state(self, buffer: dict={}, force: bool=False):
    for move in {m: buffer[m] for m in self.dict["states"] if m in buffer}:
        if force or (
            self.fet in self.dict["states"][move].get("state", "grounded")
            and (
                (
                    self.frame == [0, 0]
                    and "neutral" in self.dict["states"][move].get("cancel", [None])
                    or (
                        (
                            "kara" in self.dict["states"][move].get("cancel", [None])
                            and self.kara
                            and "kara"
                            not in self.dict["states"][self.current_state].get(
                                "cancel", [None]
                            )
                        )
                        or (
                            set(self.cancel).intersection(
                                self.dict["states"][move].get("cancel", [None])
                            )
                        )
                    )
                    and (
                        self.current_state
                        not in self.dict["states"][move].get("no_cancel_states", [])
                    )
                )
            )
            and self.gauges.get("super", 0)
            >= self.dict["states"][move].get("bar_use", 0)
        ):
            if self.dict["states"][move].get("bar_use", 0):
                self.gauges["super"] -= self.dict["states"][move]["bar_use"]
            (
                self.current_state,
                self.boxes,
                self.frame,
                self.kara,
                self.buffer_state,
                self.acceleration,
                self.con_speed,
                self.hitstun,
                self.repeat,
            ) = (
                move,
                dict(self.dict["boxes"]),
                [len(self.dict["states"][move]["framedata"]), 0],
                2,
                {},
                [0, 0],
                [0, 0],
                -1 if ("ummble" in move and self.fet == "airborne") else self.hitstun,
                0,
            )
            return self.current_state
    return False


def next_frame(self, state):
    state = default_substate | state
    if self.frame[0] <= 0:
        self.frame = [0, 0]
        return
    (
        self.image_size,
        self.image_offset,
        self.image_mirror,
        self.image_tint,
        self.image_angle,
        self.image_repeat,
        self.image_glow,
        self.draw_textures,
        self.ignore_stop,
        self.hold_on_stun,
        self.cancel,
    ) = (
        self.dict["def_image_size"],
        self.dict["def_image_offset"],
        [False, False],
        (255, 255, 255, 255),
        (0, 0, 0),
        False,
        0,
        [],
        False,
        False,
        [None],
    )
    for value in function_dict:
        if state.get(value, None) != None:
            function_dict[value](self, state[value], False)
    self.frame[0] -= 1


def object_kill(self, *args):
    """Kill the object instantly."""
    try:
        self.game.object_list.remove(self)
    except:
        pass


def object_remove_box_key(self=object, key="", *args):
    self.boxes[key[0]].pop(key[1], None)


def object_hitset(self, hitset=any, *args):
    """Enable collisions of the current hitbox, it stays at 1 and after a hit it goes back to 0."""
    self.boxes["hitbox"]["hitset"] = self.boxes["hitbox"].get("hitset", 1) - 1


def object_hit_damage(self: object, damage=(10, 0), other=object, *args):
    """Damage done to the object that has been hit. Damage on Parry is 0. 'damage':(Damage on hit, Damage on block)"""
    damage = math.ceil(
        abs(
            {
                "parry": 0,
                "block": damage[1]
                * (
                    self.self_main_object.damage_scaling[0]
                    if self.self_main_object.damage_scaling[0]
                    > self.self_main_object.damage_scaling[1]
                    else self.self_main_object.damage_scaling[1]
                )
                / 100,
                "hurt": damage[0]
                * (
                    self.self_main_object.damage_scaling[0]
                    if self.self_main_object.damage_scaling[0]
                    > self.self_main_object.damage_scaling[1]
                    else self.self_main_object.damage_scaling[1]
                )
                / 100,
            }.get(other.current_command[0], 0)
        )
    )
    other.gauges["health"], other.last_damage = other.gauges["health"] - damage, [
        other.last_damage[0] + damage if other.hitstun else damage,
        damage,
    ]


def object_hit_hitgain(self: object, gain=(5, 0), other=object, *args):
    """Special bar Gain, applies to the object that hits and the object hit. Gain on Parry is 0. 'Gain':(Gain on hit, Gain on block)"""
    self.gauges["super"] += {"parry": 0, "block": gain[0][1], "hurt": gain[0][0]}.get(
        other.current_command[0], 0
    )
    other.gauges["super"] += {"parry": 8, "block": gain[1][1], "hurt": gain[1][0]}.get(
        other.current_command[0], 0
    )


def object_hit_stamina(self: object, stamina=(0, 0), other=object, *args):
    """Stamina lost by the object hit. Stamina lost on Parry is 0. 'Stamina':(Stamina lost on hit, Stamina loston block)"""
    other.gauges["stamina"] += {
        "parry": 0,
        "block": stamina[1],
        "hurt": stamina[0],
    }.get(other.current_command[0], 0)


def object_hit_hitstun(self: object, stun=(30, 0), other=object, *args):
    """Hitstun of the object that has been hit. Hitstun on Parry is 0. 'Hitstun':(Hitstun on hit, Hitstun on block)"""
    other.hitstun = {"hurt": stun[0], "block": stun[1], "parry": 0}.get(
        other.current_command[0], 0
    )  # hitstun


def object_hit_hitstop(self: object, stop=10, other=object, *args):
    """Hitstop (Hitlag) of the hitting object and the object that has been hit. It depends on whether it is a hit, block or parry. The Hitstop advantage on parry varies for Normal, Special or Super attacks. 'Hitstop': Stop on frames"""
    type = "parry" in [
        type for type in attack_type_value if type in other.current_command
    ]
    self.hitstop, other.hitstop = 16 if type else stop, 16 if type else stop

    object_display_shake(
        other,
        [
            20 * self.face if type else other.speed[0],
            0 if type else other.speed[1],
            self.hitstop if type else other.hitstop,
            "other" if type else "self",
        ],
        self,
    )

    for active_object in self.game.object_list:
        if (
            active_object.__class__.__name__ == "Combo_Counter"
            and active_object.parent == self
        ):
            object_display_shake(
                active_object, [other.speed[0], other.speed[1], 20, "self"], self
            )


def object_hit_juggle(self: object, juggle: int = 1, other=object, *args):
    """Indicates how many hits an object can withstand while airborne. When the counter is less than 0, the hit object becomes intangible until it hits the ground. 'Juggle': Juggle number subtracted"""
    if other.fet == "airborne":
        other.juggle -= int(juggle)


def object_hit_knockback(
    self: object, knockback={"grounded": [14, 0]}, other=object, *args
):
    """The recoil of the on the object being hit. Knockback on Parry is 0. 'Knockback':(Knockback on block (X, Y), Knockback on hit (X, Y), Knockback while airborne (X, Y))"""
    speed = knockback.get("grounded", [14, 0])
    if (
        "hurt" in other.current_command[0]
        and knockback.get("airborne", False)
        and other.fet == "airborne"
    ):
        speed = knockback["airborne"]
    if "block" in other.current_command[0]:
        speed = knockback["block"] if knockback.get("block", False) else [speed[0], 0]
    if "parry" in other.current_command[0]:
        speed = knockback["parry"] if knockback.get("parry", False) else [0, 0]
    speed = [
        (speed[0] * self.face) + (self.speed[0] if len(speed) > 2 else 0),
        speed[1] + (self.speed[1] if len(speed) > 2 else 0),
    ]
    other.speed, other.fet, other.face, other.pos[1] = (
        speed,
        "airborne" if speed[1] > 0 and other.fet == "grounded" else "grounded",
        1 if self.self_main_object.pos[0] > other.pos[0] else -1,
        other.pos[1] + (10 if speed[1] > 0 and other.fet == "grounded" else 0),
    )
    if other.gauges["health"] <= 0:
        speed[1] = 20
        other.fet = "airborne"


def object_hit_hittype(
    self: object, hittype: list = ["medium", "middle"], other: object = object, *args
):
    """Determines the type of hit. Super, Special, Heavy, Medium or Light. High, Mid or Low. A specific hit type can be added to initiate a unique hit animation. 'Hittype': [hit type 1, hit type 2,,, hit type N]"""
    self.damage_scaling, other.frame = [
        self.self_main_object.damage_scaling[0]
        - attack_type_value[[type for type in attack_type_value if type in hittype][0]][
            "scaling"
        ],
        attack_type_value[[type for type in attack_type_value if type in hittype][0]][
            "min_scaling"
        ],
    ], [0, 0]
    if other.gauges["health"] <= 0:
        hittype = hittype + ["sidetummble"]
    if "hurt" in other.current_command:
        other.current_command, other.cancel, other.pos[1] = (
            other.current_command + list(hittype),
            [None],
            (
                other.pos[1] - 1
                if other.fet == "grounded"
                and self.boxes["hitbox"]
                .get("knockback", {"grounded": [14, 0]})
                .get("grounded", [14, 0])[1]
                else other.pos[1]
            ),
        )


def object_wallbounce(self: object, wallbounce=1, other=object, *args):
    """Indicates whether the hit object will bounce off walls. 'Wallbounce': Any"""
    other.wallbounce = True


def object_duration(self: object, d=0, *args):
    """The duration of the substate in frames. 'dur': duration"""
    self.frame[1] = d


def object_image(self: object, image="reencor/none", *args):
    """Name of the image displayed. It corresponds to the name of the folder followed by '/' and followed by the name of the image file. 'image': 'Name'"""
    self.image, self.real_image_size = (
        (image, self.game.image_dict[image][1])
        if image in self.game.image_dict
        else ("reencor/none", [100, 100])
    )


def object_image_size(self: object, size=(10, 10, 0), *args):
    """Name of the image displayed. It corresponds to the name of the folder followed by '/' and followed by the name of the image file. 'image': 'Name'"""
    self.image_size = size if len(size) == 3 else (size[0], size[1], 0)


def object_image_offset(self: object, image_offset=(0, 0, 0), *args):
    """image Temporal Offset. Only during the current substate. 'image_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.image_offset = (
        image_offset
        if len(image_offset) == 3
        else (image_offset[0], image_offset[1], 0)
    )


def object_image_mirror(self: object, mirror=(0, 0), *args):
    """Reflects the last loaded image. 'image_mirror': (X image_mirror 1 if true, Y image_mirror 1 if true)"""
    self.image_mirror = mirror if len(mirror) == 3 else (mirror[0], mirror[1], 0)


def object_image_tint(self: object, tint=(255, 255, 255, 255), *args):
    self.image_tint = tint


def object_image_angle(self: object, angle=(0, 0, 0), *args):
    self.image_angle = angle


def object_image_repeat(self: object, repeat=False, *args):
    self.image_repeat = repeat


def object_image_glow(self: object, glow=0, *args):
    self.image_glow = glow


def object_double_image(self: object, doim=any, *args):
    """Draw the above images on the screen. 'Double_image': Any"""
    pass


def object_draw_textures(self: object, draw_textures: list = [{}], *args):
    """Draw textures on the screen. 'draw_textures': [Texture, Texture, Texture]"""
    self.draw_textures = draw_textures


def GL_set_light(self, light=[-1, 1, -2, 0], *args):
    pass
    #glLightfv(GL_LIGHT0, GL_POSITION, light)


def GL_set_ambient(self, ambient=[0.9, 0.9, 0.9, 1], *args):
    pass
    #glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)


def object_display_shake(self: object, shake=[0, 0, 0, None], other=object, *args):
    shake[0], shake[1] = normalize_vector(shake[0], shake[1], 20)
    if shake[3] == "self":
        self.draw_shake = [0, 0, 0, shake[0], shake[1], shake[2]]
    if shake[3] == "other":
        other.draw_shake = [0, 0, 0, shake[0], shake[1], shake[2]]
    if shake[3] == "camera":
        self.game.camera.draw_shake = [0, 0, 0, shake[0], shake[1], shake[2]]


def object_voice(self: object, voice="reencor/nota", *args):
    """Plays sound from the object. This sound can be interrupted. 'folder/file name'. 'Voice': 'Name'"""
    voice = self.game.sound_dict.get(weighted_choice(voice), "none")
    if voice != "none":
        self.voice_channel.play(voice)
    else:
        pass


def object_sound(self: object, sound="reencor/nota", *args):
    """Plays sound from the object. This sound can not be interrupted. 'folder/file name'. 'Sound': 'Name'"""
    sound = self.game.sound_dict.get(sound, "none")
    if sound != "none":
        self.sound_channel.play(sound)
    else:
        pass


def object_facing(self: object, facing=1, *args):
    """Set the direction in which the object is facing. 'Facing': -1 reverses the direction the object is currently facing"""
    self.face *= facing


def object_set_relative_pos(self: object, pos=[0, 0], other: object = object, *args):
    """Changes the location of the "other" object relative on the "self" object. Does not affect speed. 'Pos': (X (Depends on where the "self" object is facing), Y)"""
    other.pos = [self.pos[0] + pos[0] * self.face, self.pos[1] + pos[1], 0]


def object_pos_offset(self: object, pos_offset=(0, 0), *args):
    """Changes the location of the object instantly. Does not affect speed. 'Pos_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.pos = [
        self.pos[0] + pos_offset[0] * self.face,
        self.pos[1] + pos_offset[1],
        self.pos[2],
    ]


def object_speed(self: object, speed=(0, 0), *args):
    """Set the absolute Speed of the object. 'Speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    self.speed = [speed[0] * self.face, speed[1]]


def object_acceleration(self: object, accel=(0, 0), *args):
    """Set the Acceleration of the object. 'Accel': (X Acceleration (Depends on where the object is facing)., Y Acceleration)"""
    self.acceleration = accel[0], accel[1]


def object_add_speed(self: object, add_speed=(0, 0), *args):
    """Adds Speed to the object. 'Add_speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    self.speed = [
        self.speed[0] + add_speed[0] * self.face,
        self.speed[1] + add_speed[1],
    ]


def object_con_speed(self: object, con_speed=(0, 0), *args):
    """Set the Speed of the object during all the current state. 'Con_speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    self.con_speed = [con_speed[0] * self.face, con_speed[1]]


def object_cancel(self: object, cancel=0, *args):
    """Set the Cancel State of the object during all the current state. 'Cancel': Any"""
    if isinstance(cancel, str):
        cancel = [cancel]
    self.cancel = cancel


def object_main_cancel(self: object, cancel=0, *args):
    """Set the Cancel State of the object during all the current state. 'Cancel': Any"""
    if isinstance(cancel, str):
        cancel = [cancel]
    self.self_main_object.cancel = cancel


def object_ignore_stop(self: object, *args):
    """Ignore the Stop or Hitstop. 'Ignore_stop': Any"""
    self.ignore_stop = True


def object_hold_on_stun(self: object, *args):
    """Hold_on_stun. 'hold_on_stun': Any"""
    self.hold_on_stun = True


def object_smear(self: object, image="reencor/none", *args):
    """Changes the current substate image to simulate a Smear. 'Smear': Any"""
    c = self.cancel
    next_frame(
        self,
        self.dict["states"][self.current_state]["framedata"][-self.frame[0]],
    )
    self.cancel = c


def object_gain(self: object, gain=0, *args):
    """Special bar Gain, applies only to the object that hits. Gain on Parry is 0. 'Gain': Number"""
    self.gauges["super"] += gain
    # reward_on(self,1)


def object_superstop(self, superstop=1, *args):
    """The Stop applies to all currently active objects. 'Superstop': Number"""
    for object in self.game.object_list:
        if object.__class__.__name__ == "BaseActiveObject" and object.type in {
            "projectile",
            "character",
            "stage",
        }:
            object.hitstop += superstop


def object_camera_path(self: object, camera_path=(), *args):
    """The path the camera will follow. 'Camera_path': ()"""
    self.game.camera_path, self.game.frame = {
        "path": tuple(camera_path["path"]),
        "object": {
            "self": self.self_main_object,
            "other": self.other_main_object,
            "global": self.game,
        }[camera_path["object"]],
    }, [0, 0]


def object_hurtbox(self: object, hurtbox={"boxes": []}, *args):
    """The boxes on an object that indicate where it can be hit."""
    self.boxes["hurtbox"] = dict(self.dict["boxes"]["hurtbox"] | hurtbox)


def object_hitbox(self: object, hitbox={"boxes": []}, *args):
    """The boxes on an object that indicate where can it hit."""
    self.boxes["hitbox"] = dict(self.dict["boxes"]["hitbox"] | hitbox)


def object_grabbox(self: object, grabbox={"boxes": []}, *args):
    """The boxes on an object that indicate where can it grab."""
    self.boxes["grabbox"] = dict(self.dict["boxes"]["grabbox"] | grabbox)


def object_pushbox(self: object, pushbox={"boxes": []}, *args):
    """The boxes on an object that indicate where it can be pushed."""
    self.boxes["pushbox"] = dict(self.dict["boxes"]["pushbox"] | pushbox)


def object_takebox(self: object, takebox={"boxes": []}, *args):
    """The boxes on an object that indicate where it can be grabed."""
    self.boxes["takebox"] = dict(self.dict["boxes"]["takebox"] | takebox)


def object_triggerbox(self: object, triggerbox={"boxes": []}, *args):
    """The boxes on an object that indicate where it can be triggered."""
    self.boxes["triggerbox"] = dict(self.dict["boxes"]["triggerbox"] | triggerbox)


def object_boundingbox(self: object, boundingbox={"boxes": []}, *args):
    """The boxes on an object that indicate the limmits."""
    self.boxes["boundingbox"] = dict(self.dict["boxes"]["boundingbox"] | boundingbox)


def object_boxes(*args):
    """List of boxes for each of the box types. Not needed outside of box types."""
    pass


def object_update_box(self=object, update_box={}, *args):
    for box in update_box:
        self.boxes[box] = self.boxes.get(box, {}) | update_box[box]


def object_guard(self: object, guard=["middle", 0], *args):
    """Set the Parry State of the object during all the current substate hurtbox. 'Guard': Any"""
    pass


def object_repeat_substate(self: object, repeat_substate=0, *args):
    """Repeat from the specified substate within the current state."""
    if self.repeat < repeat_substate[1] or repeat_substate[1] == -1:
        self.frame, self.repeat = [
            self.frame[0] + repeat_substate[0],
            0,
        ], self.repeat + 1
    if self.repeat == repeat_substate[1]:
        self.frame = [self.frame[0], 0]


def object_get_state(self: object, command=[], *args):
    """Updates the current state by searching through a state buffer."""
    get_command(
        self, self.current_command + list(self.inputdevice.current_input) + command
    )
    got_state = get_state(self, self.buffer_state)
    if got_state:
        next_frame(
            self,
            self.dict["states"][self.current_state]["framedata"][-self.frame[0]],
        )


def object_other_get_state(self: object, command=[], other=object, *args):
    """Updates the current state by searching through a state buffer."""
    get_command(
        other,
        other.current_command
        + list(other.inputdevice.current_input)
        + [self.dict["name"], self.current_state]
        + command,
    )
    got_state = get_state(other, other.buffer_state)
    if got_state:
        next_frame(
            other,
            other.dict["states"][other.current_state]["framedata"][-other.frame[0]],
        )


def object_random_state(self: object, random_state={"Stand": {"chance": 1}}, *args):
    """Updates the state instantly using the State Name."""
    state = weighted_choice(random_state)
    if self.dict["states"].get(state) != None:
        self.current_state, self.boxes, self.frame = (
            state,
            dict(self.dict["boxes"]),
            [len(self.dict["states"][state]["framedata"]), 0],
        )
        next_frame(
            self,
            self.dict["states"][self.current_state]["framedata"][-self.frame[0]],
        )


def object_trigger_state(self: object, state="Stand", *args):
    """Updates the state instantly using the State Name."""
    if self.dict["states"].get(state) != None:
        self.current_state, self.boxes, self.frame = (
            state,
            dict(self.dict["boxes"]),
            [len(self.dict["states"][state]["framedata"]), 0],
        )
        next_frame(
            self,
            self.dict["states"][self.current_state]["framedata"][-self.frame[0]],
        )


def object_influence(self: object, who=None, other=object, *args):
    if who == "other":
        self.object_influence, other.grabed = other, self
        other.grabed.frame = [0, 0]
    elif who == "global":
        game = get_object_per_class("GameObject")
        self.object_influence, other.grabed = other, game
    elif who == "camera":
        camera = get_object_per_class("Camera")
        self.object_influence, other.grabed = other, camera


def object_influence_pos(self, pos=[10, 10, 10], *args):
    if self.object_influence != None:
        self.object_influence.pos = [
            self.pos[0] + pos[0] * self.face,
            self.pos[1] - pos[1],
            0,
        ]


def object_influence_speed(self, speed=[10, 10], *args):
    if self.object_influence != None:
        self.object_influence.speed = [speed[0] * self.face, speed[1]]


def object_off_influence(self: object, *args):
    self.object_influence.grabed = None
    self.object_influence = None


def object_stop(self: object, stop=0, *args):
    """Sets the Hitstop of the current object."""
    self.hitstop = stop


def object_create_object(self: object, object_list: list = (), *args):
    """Creates a new object, projectile or any other kind of object."""
    from Util.Active_Objects import BaseActiveObject

    for new_object in object_list:
        self.game.object_list.append(
            BaseActiveObject(
                game=self.game,
                dict=(
                    self.game.object_dict[new_object[0]]
                    if type(new_object[0]) == str
                    else new_object[0]
                ),
                pos=(
                    self.pos[0] + new_object[1][0] * self.face,
                    self.pos[1] + new_object[1][1],
                ),
                face=self.face * new_object[2],
                inicial_state=new_object[3],
                palette=new_object[4] if len(new_object) > 4 else 0,
                team=self.team,
            )
        )


function_dict = {
    "remove_box_key": object_remove_box_key,
    "hitset": object_hitset,  # reset hitbox hit state
    "damage": object_hit_damage,  # damage
    "knockback": object_hit_knockback,  # knockback on object
    "hitstop": object_hit_hitstop,  # hitstop
    "hitstun": object_hit_hitstun,  # hitstun
    "stamina": object_hit_stamina,  # stun bar or stamina
    "hit_bar_gain": object_hit_hitgain,  # bar gain
    "hittype": object_hit_hittype,  # hit type force, style
    "juggle": object_hit_juggle,  # juggle counter
    "wallbounce": object_wallbounce,  # wallbounce state
    "dur": object_duration,  # duration in frames #dict
    "image": object_image,  # image image #dict
    "image_size": object_image_size,  # current image offset #dict
    "image_offset": object_image_offset,  # current image offset #dict
    "image_mirror": object_image_mirror,  # image image_mirror #function
    "image_tint": object_image_tint,  # image tint #function
    "image_angle": object_image_angle,  # image angle #function
    "image_repeat": object_image_repeat,  # image repeat #function
    "image_glow": object_image_glow,  # image glow #function
    "draw_textures": object_draw_textures,  # draw textures #function
    "double_image": object_double_image,  # draw the above images #function
    "draw_shake": object_display_shake,  # shake the screen #function
    "light": GL_set_light,  # light #function
    "ambient": GL_set_ambient,  # ambient light #function
    "music": nomatch,  # music #function
    "voice": object_voice,  # voice #function
    "sound": object_sound,  # sound #function
    "facing": object_facing,  # facing #dict
    "set_relative_pos": object_set_relative_pos,  # set relative pos #dict
    "pos_offset": object_pos_offset,  # offset object pos in first frame #dict
    "speed": object_speed,  # speed #dict
    "accel": object_acceleration,  # acceleration #dict
    "add_speed": object_add_speed,  # acceleration #dict
    "con_speed": object_con_speed,  # acceleration #dict
    "cancel": object_cancel,  # cancelable #dict
    "main_cancel": object_main_cancel,
    "guard": object_guard,
    "ignore_stop": object_ignore_stop,  # ignore hitstop #dict
    "hold_on_stun": object_hold_on_stun,  # ignore hitstop #dict
    "smear": object_smear,  # ignore hitstop #dict
    "bar_gain": object_gain,  # ignore hitstop #dict
    "superstop": object_superstop,  # stop in every object except self
    "camera_path": object_camera_path,  # camera path and zoom
    "hurtbox": object_hurtbox,  # hurtbox data #dict
    "hitbox": object_hitbox,  # hitbox data #dict
    "grabbox": object_grabbox,  # grabbox data #dict
    "pushbox": object_pushbox,  # create pushbox #dict
    "takebox": object_takebox,  # create takebox #dict
    "triggerbox": object_triggerbox,  # create takebox #dict
    "boundingbox": object_boundingbox,  # create boundingbox #dict
    "boxes": object_boxes,  # box size
    "update_box": object_update_box,  # update box data #dict
    "influence": object_influence,  # influence object #function
    "influence_pos": object_influence_pos,  # object position #function
    "influence_speed": object_influence_speed,  # object speed #function
    "off_influence": object_off_influence,  # remove influence #function
    "repeat_substate": object_repeat_substate,  # go back n frames #function
    "get_state": object_get_state,  # cancel to next move #function
    "other_get_state": object_other_get_state,  # get state for enemy #function
    "trigg_state": object_trigger_state,  # trigger specific state #function
    "random_state": object_random_state,  # random select state #function
    "stop": object_stop,  # stop #function
    "create_object": object_create_object,  # object generation #function
    "kill": object_kill,  # destroy object
}
