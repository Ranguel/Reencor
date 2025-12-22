import random
import math
import numpy
import glm

attack_type_value = {
    "parry": {"scaling": 0.10, "min_scaling": 0.10},
    "block": {"scaling": 0.10, "min_scaling": 0.20},
    "critical": {"scaling": 0.10, "min_scaling": 0.60},
    "super": {"scaling": 0.10, "min_scaling": 0.50},
    "special": {"scaling": 0.10, "min_scaling": 0.20},
    "heavy": {"scaling": 0.10, "min_scaling": 0.10},
    "medium": {"scaling": 0.09, "min_scaling": 0.10},
    "light": {"scaling": 0.08, "min_scaling": 0.10},
}


def nomatch(*args):
    pass


def normalize_length(lst, length=3, fill=0.0):
    try:
        if isinstance(lst, numpy.ndarray):
            lst = lst.tolist()
        norm = lst[:length] + [fill] * max(0, length - len(lst))
        return numpy.array(norm, dtype=numpy.float32)
    except:
        return numpy.zeros(length, dtype=numpy.float32)


def rotatate_vector(angle, vector):
    angle
    cx, cy, cz = numpy.cos(numpy.radians(angle))
    sx, sy, sz = numpy.sin(numpy.radians(angle))

    return (
        numpy.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        @ numpy.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        @ numpy.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    ) @ numpy.array(vector, dtype=numpy.float32)


def get_model_matrix(position=(0, 0), size=(0, 0), rotation=(0, 0, 0)):
    rotation_matrix = glm.mat4(1.0)
    rotation_matrix = glm.rotate(
        rotation_matrix, glm.radians(rotation[0]), glm.vec3(1, 0, 0)
    )
    rotation_matrix = glm.rotate(
        rotation_matrix, glm.radians(rotation[1]), glm.vec3(0, 1, 0)
    )
    rotation_matrix = glm.rotate(
        rotation_matrix, glm.radians(rotation[2]), glm.vec3(0, 0, 1)
    )

    model = glm.scale(
        glm.translate(glm.mat4(1.0), glm.vec3(position[0], position[1], position[2]))
        * rotation_matrix,
        glm.vec3(
            size[0],
            size[1],
            1.0,
        ),
    )

    return model


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


def get_object_per_class(object_list: list = [], class_name: str = "character"):
    for self in object_list:
        if self.__class__.__name__ == "BaseActiveObject":
            if self.type == class_name.casefold():
                return self


def get_child_object_per_class(
    object_list: list = [], class_name: str = "character", parent=None
):
    for active_object in object_list:
        if (
            active_object.__class__.__name__ == class_name
            and active_object.parent == parent
        ):
            return active_object


def normalize_vector(x, y, base=1):
    magnitude = math.sqrt(x**2 + y**2)
    if magnitude == 0:
        return [0, 1 * base]
    return [x / magnitude * base, y / magnitude * base]


def list_contains_list(main_list, sub_list=[""], turn: bool = False):
    for sub_item in sub_list:
        item_str = str(sub_item)
        if turn:
            item_str = (
                item_str.replace("right", "__temp__")
                .replace("left", "right")
                .replace("__temp__", "left")
            )
        if item_str[0] == "-":
            if item_str[1:] in main_list:
                return False
        else:
            if item_str not in main_list:
                return False

    return True


def get_command(self, current_condition: set):
    current_condition.update(
        [
            "state=" + (self.state_current),
            "hurtbox=" + (self.boxes.get("hurtbox", {}).get("condition", "stand")),
            "wallbounce="
            + ("true" if hasattr(self, "wallbounce") and self.wallbounce else "false"),
        ]
        # "defeated="
        # + (
        #     "true"
        #     if hasattr(self, "meters") and self.meters.get("health", 1) <= 0
        #     else "false"
        # ),
    )
    for state in self.dict["states"]:
        for condition in self.dict["states"][state].get("condition", []):
            if list_contains_list(
                current_condition,
                condition,
                self.rotation[1] == 180,
            ):
                self.state_buffer[state] = self.dict["states"][state].get("buffer", 1)


def get_state(self, state_buffer: dict = {}, force: bool = False):
    for state in self.dict["states"]:
        if state not in state_buffer:
            continue
        ground_condition = self.grounded == self.dict["states"][state].get(
            "grounded", self.grounded
        )
        cancel_condition = (
            self.frame == [0, 0]
            and "neutral" in self.dict["states"][state].get("cancel", [None])
            or (
                (
                    "kara" in self.dict["states"][state].get("cancel", [None])
                    and self.kara
                    and "kara"
                    not in self.dict["states"][self.state_current].get("cancel", [None])
                )
                or set(self.cancel).intersection(
                    self.dict["states"][state].get("cancel", [None])
                )
            )
            and (
                self.state_current
                not in self.dict["states"][state].get("no_cancel_states", [])
            )
        )
        cancel_type = set(self.cancel) & set(
            self.dict["states"][state].get("cancel", [None])
        )
        gauge_condition = (
            self.meters.get("super", 0) if hasattr(self, "meters") else 0
        ) >= self.dict["states"][state].get("bar_use", 0)

        if ground_condition and (force or (cancel_condition and gauge_condition)):
            if self.dict["states"][state].get("bar_use", 0):
                self.meters["super"] -= self.dict["states"][state]["bar_use"]
            # self.state_buffer.pop(state, None)
            self.state_buffer.clear()

            (
                self.state_current,
                self.boxes,
                self.frame,
                self.kara,
                self.acceleration,
                self.gravity,
                self.con_speed,
                self.repeat_substate,
            ) = (
                state,
                (
                    dict(self.dict["defaults"]["boxes"])
                    if hasattr(self, "wallbounce")
                    else {}
                ),
                [len(self.dict["states"][state]["framedata"]), 0],
                2,
                numpy.array([0, 0, 0], dtype=numpy.float32),
                numpy.array(self.dict["gravity"], dtype=numpy.float32),
                numpy.array([0, 0, 0], dtype=numpy.float32),
                0,
            )
            if (
                self.type == "character"
                and self.input_device
                and self.dict["states"][state].get("reward", 0)
            ):
                reward = float(
                    self.dict["states"][state]["reward"]
                    + (
                        0.02
                        if "interrupt" in cancel_type
                        else (
                            0.04
                            if "normal" in cancel_type
                            else 0.08 if "special" in cancel_type else 0
                        )
                    )
                )
                # self.input_device.give_reward(reward=reward, label="new state " + state)

            return self.state_current
    return False


def get_substate(self, substate: dict):
    substate = {"dur": 1} | substate
    if self.frame[0] <= 0:
        self.frame = [0, 0]
        return
    (
        self.ignore_stop,
        self.hold_on_stun,
        self.cancel,
    ) = (
        False,
        False,
        [None],
    )

    for value in function_dict:
        if substate.get(value, None) != None:
            function_dict[value](self, substate[value], False)
    self.frame[0] -= 1
    return substate


### dict func


def object_remove_box_key(self: object, value: str = "", *args, **kwargs):
    self.boxes[value[0]].pop(value[1], None)


## on hit func


def object_hitreg(self: object, other: object, tipe="hitbox", *args, **kwargs):
    """Enable collisions of the current box tipe, it stays at 1 and after a hit it goes back to 0."""
    self.boxes[tipe]["hitreg"] = self.boxes[tipe]["hitreg"] + [other]
    # self.pending_changes["hitreg"] = self.boxes[tipe]["hitreg"] + [other]


def object_hit_meter(
    self: object,
    other: object,
    value: dict = {},
    hit_result: str = "hit",
    *args,
    **kwargs
):
    scaling = self.parent.damage_scaling
    for meter, results in value.items():
        if hit_result not in results:
            continue
        for target_name, amount in results[hit_result].items():
            adjusted_amount = math.ceil(amount * scaling)
            target = self if target_name == "self" else other
            if meter in target.meters:
                target.meters[meter] += adjusted_amount
                # target.pending_changes[meter] = target.meters[meter] + adjusted_amount


def object_hitstun(
    self: object,
    other: object,
    value: dict = {},
    hit_result: str = "hit",
    strength: str = "medium",
    *args,
    **kwargs
):
    """hitstun of the object that has been hit. hitstun on Parry is 0. 'hitstun':(hitstun on hit, hitstun on block)"""
    if not other.hitstun:
        self.parent.damage_scaling, self.parent.combo_list, self.parent.combo = (
            1,
            [],
            0,
        )
    else:
        attack_values = attack_type_value.get(strength, attack_type_value["medium"])
        self.parent.damage_scaling = self.damage_scaling = max(
            self.parent.damage_scaling - attack_values["scaling"],
            attack_values["min_scaling"],
        )
        self.parent.combo += 1
        self.parent.combo_list.append(self.dict["name"] + " " + self.state_current)

    if hit_result not in value:
        value[hit_result] = value[next(iter(value))]

    if value == int and hit_result in ["hit", "block"]:
        other.pending_changes["hitstun"] = value
    else:
        other.pending_changes["hitstun"] = value.get(hit_result, 10)


def object_hitstop(self, other, value=None, hit_result="hit", *args, **kwargs):
    """
    Determines hitstop values for attacker (self) and defender (other).
    Supports:
        - int (same for both on hit / block)
        - dict: { "hit": X, "block": Y, "parry": {...} }
        - dict nested: { "hit": { "self": A, "other": B } }
    """

    # ---- DEFAULTS ----
    DEFAULT_PARRY = {"self": 16, "other": 12}

    value = value or {}

    # -------- Resolve hitstop values --------

    # Case 1: Simple integer
    if isinstance(value, int):
        if hit_result in ("hit", "block"):
            hs_self = hs_other = value
        else:  # parry
            hs_self, hs_other = DEFAULT_PARRY["self"], DEFAULT_PARRY["other"]

    # Case 2: Dict
    else:
        # If result not specified, fallback to first available key
        if hit_result not in value:
            first_key = next(iter(value))
            value[hit_result] = value[first_key]

        v = value[hit_result]

        # Case: value[hit_result] = int
        if isinstance(v, int):
            hs_self = hs_other = v

        # Case: value[hit_result] = dict
        else:
            hs_self = v.get(
                "self", DEFAULT_PARRY["self"] if hit_result == "parry" else 0
            )
            hs_other = v.get(
                "other", DEFAULT_PARRY["other"] if hit_result == "parry" else 0
            )

    # ---- Assign pending changes ----
    self.pending_changes["hitstop"] = hs_self
    other.pending_changes["hitstop"] = hs_other

    # ---- SHAKING (clean and readable) ----
    # Attacker shakes on parry
    target = self if hit_result == "parry" else other

    strength = 0.1 * (hs_other if hit_result != "parry" else 1)  # small but scaled
    duration = hs_self if hit_result == "parry" else hs_other

    direction = (
        (1, 0)
        if hit_result == "parry"
        else (other.pending_changes.get("speed", [1, 1]))
    )

    object_display_shake(
        target,
        {
            "strength": strength,
            "direction": direction,
            "duration": duration,
            "damping": 8,
        },
    )

    object_display_shake(
        get_child_object_per_class(self.app.object_list, "Combo Counter", self),
        {"shake": [int(other.speed[0]), int(other.speed[1]), 20]},
    )

    if hit_result == "parry":
        self.pending_changes[object_display_shake] = {
            "self": self,
            "value": {"shake": [0, 10, 10], "target": "camera"},
        }


def object_hit_juggle(
    self: object,
    other: object,
    value: int = 0,
    hit_result: str = "hit",
    tumble: bool = False,
    *args,
    **kwargs
):
    """Indicates how many hits an object can withstand while airborne. When the counter is less than 0, the hit object becomes intangible until it hits the ground. 'Juggle': Juggle number subtracted"""
    if (
        (not other.grounded)
        or (
            other.grounded
            and tumble.get("grounded" if other.grounded else "airborne", "no") == "hit"
        )
    ) and hit_result == "hit":
        other.pending_changes["juggle"] = other.juggle - value


def object_knockback(
    self: object,
    other: object,
    value: dict = {},
    hit_result: str = "hit",
    tumble: bool = False,
    *args,
    **kwargs
):
    """
    Knockback aplicado a 'other' cuando recibe un golpe.
    value puede estar en formato:
      - {"vec": [x, y]}
      - {"hit": {"vec": [x, y]}, "block": {"vec": [x, y]}}
      - {"hit": {"grounded": {"vec": [x, y]}, "airborne": {"vec": [x, y]}}}
    Opcional: "type": "inherit" → suma la velocidad del atacante
    """
    contact = "grounded" if other.grounded else "airborne"
    knockback = [0, 0]
    knockback_type = ""
    data = value.get(hit_result)

    if data is None:
        if hit_result == "block":
            data = value.get("hit")
        elif hit_result == "hit":
            data = value.get("block")
    if data is None:
        data = value if "vec" in value else None
    if isinstance(data, dict):
        if "vec" in data:
            knockback = data["vec"]
            knockback_type = data.get("type", "")
        elif contact in data:
            state = data[contact]
            knockback = state.get("vec", [0, 0])
            knockback_type = state.get("type", "")
    if hit_result == "block":
        knockback = [knockback[0], 0]
    elif hit_result == "parry":
        knockback = [0, 0]
        knockback_type = ""

    if knockback_type == "inherit":
        knockback = normalize_length(knockback) + rotatate_vector(
            self.rotation, self.speed
        )

    other.pending_changes["speed"] = rotatate_vector(
        self.rotation, normalize_length(knockback)
    ) + numpy.array(
        [
            0,
            0.2 if (other.meters.get("health", 1) <= 0 and knockback[1] == 0) else 0,
            0,
        ],
        dtype=numpy.float32,
    )

    if (
        tumble.get("grounded" if other.grounded else "airborne", "no") == hit_result
        or other.meters.get("health", 1) <= 0
    ) and other.grounded:
        other.pending_changes["grounded"], other.pending_changes["position"] = (
            False,
            other.position + numpy.array([0, 0.1, 0]),
        )


def object_damage(
    self: object,
    other: object,
    value: dict = {} or int,
    hit_result: str = "hit",
    *args,
    **kwargs
):
    """Damage applied to 'other' when hit. 'Damage': Number"""
    if isinstance(value, int):
        other.meters["health"] -= value * self.parent.damage_scaling
        return

    if hit_result in value:
        other.meters["health"] -= value[hit_result] * self.parent.damage_scaling

    return
    if isinstance(value, int):
        other.pending_changes["meters"] = {
            "health": other.meters.get("health", 0)
            - (value * self.parent.damage_scaling)
        }
        return

    if hit_result in value:
        other.pending_changes["meters"] = {
            "health": other.meters.get("health", 0)
            - (value[hit_result] * self.parent.damage_scaling)
        }


def object_anim_on_hit(
    self: object,
    other: object,
    value: str = "middle",
    hit_result: str = "hit",
    strength: str = "medium",
    reaction: str = "normal",
    tumble: bool = False,
    *args,
    **kwargs
):
    """Determines the type of hit.
    Examples: Super, Special, Heavy, Medium, Light, High, Mid, Low.
    A specific hit type can trigger a unique hit animation.
    'value': [hit_type_1, hit_type_2, ...]"""

    other.current_condition.update(
        [
            hit_result,
            "level=" + value,
            "strength=" + strength,
            "reaction=" + reaction,
            (
                "tumble=true"
                if tumble.get("grounded" if other.grounded else "airborne", "no")
                == hit_result
                else ""
            ),
        ]
    )
    if other.meters.get("health", 1) <= 0:
        other.current_condition.update(["reaction=hook", "tumble=true"])

    (
        other.pending_changes[object_other_get_state],
        self.pending_changes["current_condition"],
        other.pending_changes["rotation"],
    ) = (
        {
            "self": self,
            "value": {
                "condition": other.current_condition,
                "force": True,
            },
            "other": other,
        },
        self.current_condition | {"did_" + hit_result},
        numpy.array(
            [
                other.rotation[0],
                180 if (self.rotation[1] == 0) else 0,
                other.rotation[2],
            ],
            dtype=numpy.float32,
        ),
    )


def object_hit_wallbounce(self: object, value=1, other=object, *args, **kwargs):
    """Indicates whether the hit object will bounce off walls. 'Wallbounce': Any"""
    # other.wallbounce = True
    other.pending_changes["wallbounce"] = True


def object_state_on_hit(
    self: object,
    value: dict = {"hit": "", "block": "", "parry": ""},
    hit_result: str = "hit",
    *args,
    **kwargs
):
    """Updates the state instantly using the State Name."""
    state = get_state(self, state_buffer={value.get(hit_result, "none"): 1}, force=True)
    if state:
        get_substate(
            self,
            substate=self.dict["states"][self.state_current]["framedata"][
                -self.frame[0]
            ],
        )


def object_pos_on_hit(
    self: object,
    value={"hit": {"vec": [0, 0]}, "block": {"vec": [0, 0]}, "parry": {"vec": [0, 0]}},
    hit_result: str = "hit",
    other: object = object,
    *args,
    **kwargs
):
    """Changes the location of the "other" object relative on the "self" object. Does not affect speed. 'position': (X (Depends on where the "self" object is facing), Y)"""
    if hit_result in value:
        other.pending_changes["position"] = self.position + rotatate_vector(
            self.rotation, normalize_length(value[hit_result]["vec"])
        )


## self func


def object_duration(self: object, value=0, *args, **kwargs):
    """The duration of the substate in frames. 'dur': duration"""
    self.frame[1] = value


def object_draw(self: object, value: list = [{}], *args, **kwargs):
    """Draw textures on the screen. 'draw': [Texture, Texture, Texture]"""
    self.draw = value
    self.render_interruption = True


def object_double_image(self: object, value=any, *args, **kwargs):
    """Draw the above images on the screen. 'Double_image': Any"""
    pass


def GL_set_light(self, value=[-1, 1, -2, 0], *args, **kwargs):
    pass
    # glLightfv(GL_LIGHT0, GL_POSITION, light)


def GL_set_ambient(self, value=[0.9, 0.9, 0.9, 1], *args, **kwargs):
    pass
    # glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)


def object_display_shake(
    self: object,
    value: dict = {
        "strength": 20,
        "direction": [0, 0],
        "duration": None,
        "damping": 6,
        "target": "self",
    },
    *args,
    **kwargs
):
    target = self if value.get("target", "self") == "self" else self.app.renderer.camera
    if target == None:
        return

    target.draw_shake.trigger(
        strength=value.get("strength", 0.2),
        direction=rotatate_vector(
            self.rotation, normalize_length(value.get("direction", [1, 1]))
        ),
        duration=value.get("duration", None),
        damping=value.get("damping", 6.0),
    )


def object_voice(self: object, value="reencor/nota", *args, **kwargs):
    """Plays sound from the object. This sound can be interrupted. 'folder/file name'. 'Voice': 'Name'"""
    value = self.app.sound_dict.get(weighted_choice(value), "none")
    if value != "none":
        self.voice_channel.play(value)
    else:
        pass


def object_sound(self: object, value="reencor/nota", *args, **kwargs):
    """Plays sound from the object. This sound can not be interrupted. 'folder/file name'. 'Sound': 'Name'"""
    value = self.app.sound_dict.get(value, "none")
    if value != "none":
        self.sound_channel.play(value)
    else:
        pass


def object_facing(self: object, value=1, *args, **kwargs):
    """Set the direction in which the object is facing. 'Facing': -1 reverses the direction the object is currently facing"""
    self.rotation[0] = 0 if value == 1 else 180


def object_set_pos_on_hit(
    self: object, value={"vec": [0, 0]}, other: object = object, *args, **kwargs
):
    """Changes the location of the "other" object relative on the "self" object. Does not affect speed. 'position': (X (Depends on where the "self" object is facing), Y)"""
    other.position = self.position + rotatate_vector(
        self.rotation, normalize_length(value["vec"])
    )


def object_pos_offset(self: object, value={"vec": [0, 0]}, *args, **kwargs):
    """Changes the location of the object instantly. Does not affect speed. 'Pos_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.position += rotatate_vector(
        self.rotation,
        normalize_length(value["vec"]),
    )


def object_pushback(self: object, value=[0, 0], *args, **kwargs):
    """Changes the location of the object instantly. Does not affect speed. 'Pos_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.position += normalize_length(value)


def object_speed(
    self: object, value: dict = {"vec": [0, 0], "type": "set"}, *args, **kwargs
):
    """Set the absolute Speed of the object. 'Speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    if value.get("type", "set") == "set":
        self.speed = rotatate_vector(
            self.rotation, normalize_length(value.get("vec", [0, 0]))
        )
    elif value.get("type", "") == "add":
        self.speed += rotatate_vector(
            self.rotation, normalize_length(value.get("vec", [0, 0]))
        )
    elif value.get("type", "") == "constant":
        self.con_speed = numpy.array(
            normalize_length(value.get("vec", [0, 0])),
            dtype=numpy.float32,
        )


def object_acceleration(self: object, value={"vec": [0, 0]}, *args, **kwargs):
    """Set the Acceleration of the object. 'Accel': (X Acceleration (Depends on where the object is facing)., Y Acceleration)"""
    self.acceleration = rotatate_vector(self.rotation, normalize_length(value["vec"]))


def object_gravity(self: object, value={"vec": [0, -0.1]}, *args, **kwargs):
    """Set the Gravity of the object. 'Gravity': (X Gravity (Depends on where the object is facing)., Y Gravity)"""
    self.gravity = numpy.array(normalize_length(value["vec"]), dtype=numpy.float32)


def object_cancel(self: object, value="", *args, **kwargs):
    """Set the Cancel State of the object during all the current state. 'Cancel': Any"""
    if isinstance(value, str):
        value = [value]
    self.cancel = value


def object_main_cancel(self: object, value=0, *args, **kwargs):
    """Set the Cancel State of the object during all the current state. 'Cancel': Any"""
    if isinstance(value, str):
        value = [value]
    self.parent.cancel = value


def object_ignore_stop(self: object, *args, **kwargs):
    """Ignore the Stop or hitstop. 'Ignore_stop': Any"""
    self.ignore_stop = True


def object_hold_on_stun(self: object, *args, **kwargs):
    """Hold_on_stun. 'hold_on_stun': Any"""
    self.hold_on_stun = True


def object_smear(self: object, value="reencor/none", *args, **kwargs):
    """Changes the current substate image to simulate a Smear. 'Smear': Any"""
    c = self.cancel
    get_substate(
        self,
        self.dict["states"][self.state_current]["framedata"][-self.frame[0]],
    )
    self.cancel = c


def object_gain(self: object, value: int = 0, *args, **kwargs):
    """Special bar Gain, applies only to the object that hits. Gain on Parry is 0. 'Gain': Number"""
    self.meters["super"] += value
    # reward_on(self,1)


def object_superstop(self, value: int = 1, *args, **kwargs):
    """The Stop applies to all currently active objects. 'Superstop': Number"""
    for object in self.app.object_list:
        if object.__class__.__name__ == "BaseActiveObject" and object.type in {
            "projectile",
            "character",
            "stage",
        }:
            object.hitstop += value


def object_camera_path(self: object, value: list = [], *args, **kwargs):
    """The path the camera will follow. 'Camera_path': ()"""
    self.app.camera_path, self.app.frame = {
        "path": tuple(value["path"]),
        "object": {
            "self": self.parent,
            "other": self.rival,
            "global": self.app,
        }[value["object"]],
    }, [0, 0]


def object_boxes(self=object, value: dict = {}, *args, **kwarg):
    """List of boxes for each of the box types. Not needed outside of box types."""
    for box_type in value:
        try:
            if box_type in self.boxes:
                self.boxes[box_type] = dict(
                    self.boxes.get(box_type, {}) | value[box_type]
                )
        except:
            pass
            # print("box err", value, self.boxes)


def object_guard(self: object, value: list = ["middle", 0], *args, **kwargs):
    """Set the Parry State of the object during all the current substate hurtbox. 'Guard': Any"""
    pass


def object_repeat_substate(self: object, value: int = 0, *args, **kwargs):
    """Repeat from the specified substate within the current state."""
    if self.repeat_substate < value[1] or value[1] == -1:
        self.frame, self.repeat_substate = [
            self.frame[0] + value[0],
            0,
        ], self.repeat_substate + 1
    if self.repeat_substate == value[1]:
        self.frame = [self.frame[0], 0]


def object_get_state(
    self: object, value: dict = {"condition": [], "force": False}, *args, **kwargs
):
    """Updates the current state by searching through a state buffer."""
    get_command(
        self,
        current_condition=self.input
        | set(self.current_condition)
        | set(value.get("condition", [])),
    )
    state = get_state(
        self, state_buffer=self.state_buffer, force=value.get("force", False)
    )
    if state:
        get_substate(
            self,
            substate=self.dict["states"][self.state_current]["framedata"][
                -self.frame[0]
            ],
        )
    return state


def object_other_get_state(
    self: object,
    value: dict = {"condition": [], "force": False},
    other=object,
    *args,
    **kwargs
):
    """Updates the current state by searching through a state buffer."""
    get_command(
        other,
        current_condition=other.input
        | other.current_condition
        | set(value.get("condition", [])),
    )
    state = get_state(
        other, state_buffer=other.state_buffer, force=value.get("force", False)
    )
    if state:
        get_substate(
            other,
            substate=other.dict["states"][other.state_current]["framedata"][
                -other.frame[0]
            ],
        )
    return state


def object_random_state(
    self: object, value: dict = {"Stand": {"chance": 1}}, *args, **kwargs
):
    """Updates the state instantly using the State Name."""
    random_state = weighted_choice(value)
    state = get_state(self, state_buffer={random_state: 2}, force=True)
    if state:
        get_substate(
            self,
            substate=self.dict["states"][self.state_current]["framedata"][
                -self.frame[0]
            ],
        )
    return state


def object_trigger_state(self: object, value: str = "Stand", *args, **kwargs):
    """Updates the state instantly using the State Name."""
    state = get_state(self, state_buffer={value: 1}, force=True)
    if state:
        get_substate(
            self,
            substate=self.dict["states"][self.state_current]["framedata"][
                -self.frame[0]
            ],
        )


def object_influence(self: object, value: str = "", other=object, *args, **kwargs):
    if value == "other":
        self.object_influence, other.grabed = other, self
        other.grabed.frame = [0, 0]
    elif value == "global":
        game = get_object_per_class("GameObject")
        self.object_influence, other.grabed = other, game
    elif value == "camera":
        camera = get_object_per_class("Camera")
        self.object_influence, other.grabed = other, camera


def object_influence_pos(self, value: list = [10, 10, 10], *args, **kwargs):
    if self.object_influence != None:
        self.object_influence.position = self.position + rotatate_vector(
            self.rotation, value if len(value) == 3 else (value[0], value[1], 0)
        )


def object_influence_speed(self, value: list = [10, 10], *args, **kwargs):
    if self.object_influence != None:
        self.object_influence.speed = [value[0], value[1], 0]


def object_off_influence(self: object, *args, **kwargs):
    self.object_influence.grabed = None
    self.object_influence = None


def object_stop(self: object, value: int = 0, *args, **kwargs):
    """Sets the hitstop of the current object."""
    self.hitstop = value


def object_create_object(self, value=None, *args, **kwargs):
    from engine.gameplay.active_objects import BaseActiveObject

    if not value:
        return

    for obj in value:
        inherit = obj.get("inherit", True)
        base_dict = self.app.object_dict.get(obj.get("dict", "none"))

        pos = normalize_length(obj.get("position", {}).get("vec", [0, 0]))
        rot = normalize_length(obj.get("rotation", [0, 0]))
        spd = normalize_length(obj.get("speed", {}).get("vec", [0, 0]))

        if inherit:
            pos = self.position + rotatate_vector(self.rotation, pos)
            rot = self.rotation + rot
            spd = self.speed + rotatate_vector(self.rotation, spd)

        new = BaseActiveObject(
            app=self.app,
            dict=base_dict,
            position=pos,
            rotation=rot,
            # speed=spd,
            state=obj.get("state", "none"),
            condition=obj.get("condition", ["x_neutral", "y_neutral"]),
            palette=obj.get("palette", 0),
            team=self.team,
            parent=self,
        )

        self.app.object_list.append(new)


def object_kill(self: object, *args, **kwargs):
    """Kill the object instantly."""
    try:
        # self.app.object_list.remove(self)
        self.pending_changes[remove_pending_kill] = {"self": self}

    except:
        pass


def remove_pending_kill(self: object):
    try:
        self.app.object_list.remove(self)
    except:
        pass


def apply_pending_changes(self: object):
    for key, value in self.pending_changes.items():
        if callable(key):
            key(**value)
        else:
            setattr(self, key, value)

    self.pending_changes.clear()


function_dict = {
    "remove_box_key": object_remove_box_key,
    # on hit (self, other, value, hit_result)
    "hitreg": object_hitreg,  # reset hitbox hit state
    "knockback": object_knockback,  # knockback on object
    "hitstop": object_hitstop,  # hitstop
    "hitstun": object_hitstun,  # hitstun
    "damage": object_damage,  # damage on object
    "hit_meter": object_hit_meter,
    "level": object_anim_on_hit,  # hit type force, style
    "state_on_hit": object_state_on_hit,
    "pos_on_hit": object_pos_on_hit,  # set relative position #dict
    "juggle": object_hit_juggle,  # juggle counter
    "wallbounce": object_hit_wallbounce,  # wallbounce state
    # general (self, value)
    "dur": object_duration,  # duration in frames #dict
    "draw": object_draw,  # draw textures #function
    "double_image": object_double_image,  # draw the above images #function
    "draw_shake": object_display_shake,  # shake the screen #function
    "light": GL_set_light,  # light #function
    "ambient": GL_set_ambient,  # ambient light #function
    "music": nomatch,  # music #function
    "voice": object_voice,  # voice #function
    "sound": object_sound,  # sound #function
    "facing": object_facing,  # facing #dict
    "pos_offset": object_pos_offset,  # offset object position in first frame #dict
    "pushback": object_pushback,  # pushback object position #dict
    "speed": object_speed,  # speed #dict
    "accel": object_acceleration,  # acceleration #dict
    "gravity": object_gravity,  # gravity #dict
    "cancel": object_cancel,  # cancelable #dict
    "main_cancel": object_main_cancel,
    "guard": object_guard,
    "ignore_stop": object_ignore_stop,  # ignore hitstop #dict
    "hold_on_stun": object_hold_on_stun,  # ignore hitstop #dict
    "smear": object_smear,  # ignore hitstop #dict
    "bar_gain": object_gain,  # ignore hitstop #dict
    "superstop": object_superstop,  # stop in every object except self
    "camera_path": object_camera_path,  # camera path and zoom
    "boxes": object_boxes,  # box size
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
