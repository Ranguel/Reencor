import numpy

from engine.gameplay.common_functions import (
    get_state,
    get_substate,
    apply_pending_changes,
    get_command,
    get_object_per_team,
    object_get_state,
    object_kill,
    rotatate_vector,
    normalize_length,
    RoundSign,
    get_model_matrix,
)
from engine.effects.shake import ShakeComponent


colors = {
    "hurtbox": (0.1, 0.1, 1, 1),
    "hitbox": (1, 0.1, 0.1, 1),
    "takebox": (0.1, 1, 1, 1),
    "grabbox": (0.1, 1, 0.1, 1),
    "pushbox": (1, 0, 1, 1),
    "triggerbox": (1, 0.5, 0, 1),
    "environmentbox": (1, 1, 1, 1),
}


class BaseActiveObject:
    def __init__(
        self,
        app: object = object,
        dict: dict = {},
        state: str = "none",
        condition: set = {},
        palette: int = 0,
        position: numpy.array = numpy.array([0, 0, 0], dtype=numpy.float32),
        rotation: numpy.array = numpy.array([0, 0, 0], dtype=numpy.float32),
        scale: numpy.array = numpy.array([1, 1, 0], dtype=numpy.float32),
        team: int = 0,
        side: bool = False,
        parent: object = None,
        kill: bool = False,
    ):
        (
            self.app,
            self.type,
            self.dict,
            self.team,
            self.side,
            self.position,
            self.scale,
            self.rotation,
            self.speed,
            self.palette,
            self.parent,
        ) = (
            app,
            dict.get("type", "none").casefold(),
            dict,
            team,
            side,
            position,
            scale,
            rotation,
            numpy.array([0, 0, 0], dtype=numpy.float32),
            palette,
            parent if parent != None else self,
        )
        (
            self.draw,
            self.draw_shake,
        ) = (
            [],
            ShakeComponent(),
        )
        self.mass, self.scale, self.time_kill, self.meters, self.boxes = (
            self.dict["mass"],
            self.dict["scale"],
            self.dict["timekill"],
            {
                meter: self.dict["meters"][meter]["inicial"]
                for meter in self.dict["meters"]
            },
            self.dict["defaults"]["boxes"],
        )
        if kill:
            self.time_kill = kill
        (
            self.frame,
            self.repeat_substate,
            self.ignore_stop,
            self.hold_on_stun,
            self.hitstun,
            self.hitstop,
        ) = ([0, 0], 0, False, False, 0, 0)
        (
            self.acceleration,
            self.gravity,
            self.con_speed,
            self.air_time,
            self.air_max_height,
        ) = (
            numpy.array([0, 0, 0], dtype=numpy.float32),
            numpy.array([0, 0, 0], dtype=numpy.float32),
            numpy.array([0, 0, 0], dtype=numpy.float32),
            0,
            0,
        )
        (
            self.grounded,
            self.grabed,
            self.cancel,
            self.kara,
            self.state_current,
            self.current_condition,
            self.state_buffer,
            self.wallbounce,
        ) = (False, None, [0], 0, state, set(condition), {}, False)
        (
            self.combo,
            self.parry,
            self.guard,
            self.juggle,
            self.damage_scaling,
            self.last_damage,
        ) = (0, ["6", 0], "", 100, 1, [0, 0])
        self.move_raw_input = {
            move: []
            for move in self.dict["states"]
            if self.dict["states"][move].get("command", False)
        }
        (
            self.rival,
            self.influence_object,
            self.combo_list,
        ) = (None, None, [])

        self.input_device = None
        self.input_interruption = False
        self.input = {"x_neutral", "y_neutral"}
        self.command = {""}

        self.pending_changes = {}
        self.state_list = list(self.dict["states"].keys())

        self.last_position = numpy.array(self.position, dtype=numpy.float32)
        self.last_rotation = numpy.array(self.rotation, dtype=numpy.float32)
        self.last_scale = numpy.array(self.scale, dtype=numpy.float32)

        self.render_interruption = True
        self.render_list = []

        if state == "none":
            state = object_get_state(self, value={"force": True})
        else:
            state = get_state(self, {state: 2}, 1)
            if state:
                get_substate(
                    self, self.dict["states"][self.state_current]["framedata"][0]
                )

    def update(self, *args):
        apply_pending_changes(self)
        if self.rival == None:
            self.rival = get_object_per_team(self.app.object_list, self.team)

        if (
            (
                ("left" in self.input and self.rotation[1] == 180)
                or ("right" in self.input and self.rotation[1] == 0)
                or "down" in self.input
            )
            and self.input_interruption
            and self.parry[1] == 0
        ):
            self.parry = ["self.input[:2]", 24]

        self.parry[1] = self.parry[1] - 1 if self.parry[1] else 0
        for meter in self.meters:
            if self.meters[meter] < 0:
                self.meters[meter] = 0
            if self.meters[meter] > self.dict["meters"][meter]["max"]:
                self.meters[meter] = self.dict["meters"][meter]["max"]

        if (not self.hitstop) and (self.grabed == None):
            if self.hitstun and self.boxes["hurtbox"].get("condition", "") != "tumble":
                self.hitstun -= 1
            if self.rival != None and self.type == "character":
                new_face = RoundSign(self.rival.position[0] - self.position[0])
                if (
                    self.grounded
                    and (
                        set(self.cancel).intersection(["neutral"])
                        or self.frame == [0, 0]
                    )
                    and new_face != RoundSign(-1 if self.rotation[1] == 180 else 1)
                    and abs(self.rival.position[0] - self.position[0]) > 0.3
                ):
                    self.rotation[1] = 180 if new_face == -1 else 0
                    self.current_condition.update(["turn"])
                    self.input_interruption = 1

            self.speed += (
                self.acceleration
                + rotatate_vector(self.rotation, self.con_speed)
                + self.gravity
            )
            self.position += self.speed

            self.state_buffer = {
                timer: self.state_buffer[timer] - 1
                for timer in self.state_buffer
                if self.state_buffer[timer] > 0
            }

        if (
            self.input_interruption
            or (self.frame[0] <= 0 and self.frame[1] <= 0)
            or (not set(self.cancel).intersection([None]) or self.kara)
        ):
            get_command(
                self,
                current_condition=self.input | self.command | self.current_condition,
            )
        if (
            (self.input_interruption or self.state_buffer)
            and (self.hitstop == 0 or self.hitstop and self.ignore_stop)
        ) or (self.frame[0] <= 0 and self.frame[1] <= 0):
            get_state(self, self.state_buffer)
        self.frame[1] -= 1 * (
            ((self.hitstop and self.ignore_stop) or (not self.hitstop))
            and ((self.hold_on_stun and not self.hitstun) or (not self.hold_on_stun))
        )
        if self.frame[1] <= 0:
            get_substate(
                self,
                self.dict["states"][self.state_current]["framedata"][-self.frame[0]],
            )

        if self.hitstop:
            self.hitstop = self.hitstop - 1
        if self.kara:
            self.kara -= 1

        if self.input_interruption:
            self.input_interruption = False

        self.current_condition.clear()

        if type(self.time_kill) != bool:
            self.time_kill -= 1
            if self.time_kill == 0:
                object_kill(self)

        if (
            numpy.any(self.position != self.last_position)
            or numpy.any(self.rotation != self.last_rotation)
            or numpy.any(self.scale != self.last_scale)
        ):
            self.render_interruption = True

        self.last_position = numpy.array(self.position, dtype=numpy.float32)
        self.last_rotation = numpy.array(self.rotation, dtype=numpy.float32)
        self.last_scale = numpy.array(self.scale, dtype=numpy.float32)

    def render(self, renderer, *args):
        if not self.render_interruption:
            renderer.draw_queue.extend(self.render_list)
            return

        self.render_interruption = False
        self.render_list = [self._build_draw_command(texture) for texture in self.draw]

        renderer.draw_queue.extend(self.render_list)

    def _build_draw_command(self, texture):
        """Create a render dictionary for a single texture entry."""

        file = texture.get("file", "")
        defaults = self.dict["defaults"]["draw"]

        # get texture file or fallback
        image_file = self.app.image_dict.get(file, self.app.image_dict["reencor/none"])
        texture_data, texture_size = image_file

        # compute shake & texture offset
        shake_offset = numpy.array(self.draw_shake.update(0.016), dtype=numpy.float32)
        texture_offset = numpy.array(
            normalize_length(texture.get("offset", defaults["offset"])),
            dtype=numpy.float32,
        )

        # generate model matrix
        position = self.position + rotatate_vector(
            self.rotation, shake_offset + texture_offset
        )
        size = self.scale * numpy.array(
            normalize_length(texture.get("size", defaults["size"])),
            dtype=numpy.float32,
        )
        rotation = self.rotation + numpy.array(
            normalize_length(texture.get("rotation", defaults["rotation"])),
            dtype=numpy.float32,
        )
        model = get_model_matrix(position=position, size=size, rotation=rotation)

        # build final render dictionary
        return {
            "color_texture": texture_data,
            "model": model,
            "flip": texture.get("flip", defaults["flip"]),
            "tint": texture.get("tint", defaults["tint"]),
            "uv_scale": texture.get("uv_scale", defaults["uv_scale"]),
            "glow": texture.get("glow", defaults["glow"]),
            "shadow_cast": texture.get("shadow_cast", defaults["shadow_cast"]),
            "disable_depth_test": texture.get(
                "disable_depth_test", defaults["disable_depth_test"]
            ),
            "program": texture.get("program", defaults["program"]),
        }

    def draw_boxes(self):
        if self.type in {
            "projectile",
            "character",
            "stage",
        }:
            for boxes_type in self.boxes:
                for box in self.boxes[boxes_type].get("rects", []):
                    model = get_model_matrix(
                        position=self.position
                        + rotatate_vector(
                            self.rotation,
                            numpy.array(
                                (box["vec"][0], box["vec"][1], 0),
                                dtype=numpy.float32,
                            ),
                        ),
                        size=(box["vec"][2], box["vec"][3]),
                        rotation=self.rotation,
                    )

                    render_cmd = {
                        "model": model,
                        "color": colors[boxes_type],
                        "transparent": 0.1,
                        "size": (box["vec"][2], box["vec"][3]),
                        "border_thickness": 0.02,
                        "disable_depth_test": True,
                        "program": "box",
                    }

                    self.app.renderer.draw_queue.append(render_cmd)


def reset_CharacterActiveObject(*args):
    pass
