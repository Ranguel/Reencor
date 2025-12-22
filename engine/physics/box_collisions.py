import numpy
import random

from engine.gameplay.active_objects import BaseActiveObject
from engine.gameplay.common_functions import (
    object_display_shake,
    object_get_state,
    object_pushback,
    object_create_object,
    function_dict,
    normalize_length,
    get_model_matrix,
    rotatate_vector,
)

default_hitbox = {
    "hitstun": {"hit": 40, "block": 38},
    "hitstop": {"hit": 9, "block": 9, "parry": {"self": 16, "other": 14}},
    "juggle": 2,
    "knockback": {"hit": {"grounded": [0, 0]}},
    "strength": "medium",
    "level": "middle",
    "reaction": "normal",
    "tumble": {"grounded": "no", "airborne": "no"},
}


boxes_pair = {
    "hitbox": "hurtbox",
    "takebox": "grabbox",
    "triggerbox": "hurtbox",
    "environmentbox": "environmentbox",
    "pushbox": "pushbox",
}


def world_rect(obj, rect):
    x = (
        obj.position[0]
        + rect[0] * (1 if obj.rotation[1] == 0 else -1)
        - rect[2] * (obj.rotation[1] == 180)
    )
    y = obj.position[1] + rect[1]
    return x, y, rect[2], rect[3]


def hit_logic(game, self, other, hitbox):
    hit_result, ri, ru = ("hit", 0.2, -0.15)
    if (
        set(other.cancel).intersection(("neutral", "interruption", "blocking"))
        and other.grounded
        and (
            ("left" in other.input and other.rotation[1] == 0)
            or ("right" in other.input and other.rotation[1] == 180)
        )
    ) or other.guard == "block":
        if hitbox["level"] in ("high", "middle") and "down" not in other.input:
            hit_result, ri, ru = "block", 0.25, 0.2
        else:
            ri, ru = 0.3, -0.2
        if hitbox["level"] in ("low", "middle") and "down" in other.input:
            hit_result, ri, ru = "block", 0.25, 0.2
        else:
            ri, ru = 0.3, -0.2

    if (
        set(other.cancel).intersection(("neutral", "interruption", "blocking", "parry"))
        and other.grounded
        and other.parry[1] >= 16
    ) or other.guard == "parry":
        if (
            hitbox["level"] in ("high", "middle")
            and (
                ("left" in other.input and other.rotation[1] == 180)
                or ("right" in other.input and other.rotation[1] == 0)
            )
            and "y_neutral" in other.input
        ):
            hit_result, ri, ru = "parry", 0.1, 0.4
            other.parry[1] = 0
        else:
            ri, ru = 0.35, -0.25
        if (
            hitbox["level"] in ("low", "middle")
            and "x_neutral" in other.input
            and "down" in other.input
        ):
            hit_result, ri, ru = "parry", 0.1, 0.4
            other.parry[1] = 0
        else:
            ri, ru = 0.35, -0.25

    # hit_result, ri, ru = "parry", 0.1, 0.4

    return hit_result, ri, ru


def rect_collide(self, other, s_rect=None, o_rect=None):
    if not s_rect or not o_rect:
        return False
    if s_rect[2] <= 0 or s_rect[3] <= 0:
        return False
    if o_rect[2] <= 0 or o_rect[3] <= 0:
        return False

    (r1x, r1y, r1w, r1h), (r2x, r2y, r2w, r2h) = world_rect(self, s_rect), world_rect(
        other, o_rect
    )

    if not (
        r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y
    ):
        return False
    pen = {
        "right": (r1x + r1w) - r2x,
        "left": (r2x + r2w) - r1x,
        "down": (r1y + r1h) - r2y,
        "up": (r2y + r2h) - r1y,
    }
    direction = min(pen, key=pen.get)
    inter_left = max(r1x, r2x)
    inter_right = min(r1x + r1w, r2x + r2w)
    inter_top = max(r1y, r2y)
    inter_bottom = min(r1y + r1h, r2y + r2h)
    center = (
        (inter_left + inter_right) * 0.5,
        (inter_top + inter_bottom) * 0.5,
    )

    return direction, center, r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h


def environmentbox_collision(game, self: BaseActiveObject, other: BaseActiveObject):
    if "stage" not in {self.type, other.type}:
        return
    if self.dict["physics_type"] == "static":
        return

    touch_ground = False

    for s_rect in self.boxes["environmentbox"].get("rects", []):
        for o_rect in other.boxes["environmentbox"].get("rects", []):
            colision = rect_collide(self, other, s_rect["vec"], o_rect["vec"])
            if not colision:
                continue
            (
                direction,
                center,
                s_rect_L,
                s_rect_D,
                s_rect_W,
                s_rect_H,
                o_rect_L,
                o_rect_D,
                o_rect_W,
                o_rect_H,
            ) = colision

            # ───────────── GROUNDED ─────────────
            if direction == "up":
                touch_ground = True
                if not self.grounded and not self.grabed and self.hitstop == 0:
                    (
                        self.grounded,
                        self.frame,
                        self.juggle,
                        self.wallbounce,
                        self.hitstun,
                        self.air_time,
                    ) = (True, [0, 0], 100, False, 0, 0)
                    self.current_condition.update(["landed"])
                    if self.boxes["hurtbox"].get("condition") == "tumble":
                        object_display_shake(
                            self,
                            {"strength": 0.2, "direction": [0, 1], "target": "camera"},
                        )
                    object_get_state(self, value={"force": True})
                if not self.hitstop:
                    friction = (
                        self.boxes["environmentbox"].get("grounded_friction", 0.7)
                        if not self.hitstun
                        else 0.85
                    )
                    self.speed[0] *= friction
                self.position[1], self.speed[1] = (
                    o_rect_D + o_rect_H - s_rect["vec"][1] - 0.001
                ), max(self.speed[1], 0)

            # ───────────── CEILING ─────────────
            elif direction == "down":
                self.position[1] = o_rect_D - s_rect_H - s_rect["vec"][1]
                self.current_condition.update(["hit_ceiling"])

            # ───────────── WALLS ─────────────
            elif direction in ("left", "right"):
                self.current_condition.update(["hit_wall"])

                if direction == "right":
                    self.position[0] = o_rect_L - s_rect_W / 2
                else:
                    self.position[0] = o_rect_L + o_rect_W + s_rect_W / 2

                if self.wallbounce and not self.grounded:
                    self.rotation[1] = 0 if direction == "right" else 180
                    self.speed = (
                        [-0.15, 0.3, 0] if direction == "right" else [0.15, 0.3, 0]
                    )
                    object_display_shake(
                        self,
                        {
                            "strength": 0.2,
                            "direction": [1, 0],
                            "target": "camera",
                        },
                    )
                    object_get_state(self, value={"force": True})
                    self.wallbounce = False

    # ───────────── AIRBORNE ─────────────
    if not touch_ground:
        if self.grounded:
            self.input_interruption = 1
        self.grounded, self.air_time, self.speed = (
            False,
            self.air_time + 1,
            self.speed
            * numpy.array(
                normalize_length(
                    self.boxes["environmentbox"].get("airborne_friction", [1, 1, 1])
                ),
                dtype=numpy.float32,
            ),
        )

    return {"tipe": "environmentbox", "touch_ground": touch_ground}


def pushbox_collision(game, self, other):
    for s_rect in self.boxes["pushbox"].get("rects", []):
        for o_rect in other.boxes["pushbox"].get("rects", []):
            collition = rect_collide(self, other, s_rect["vec"], o_rect["vec"])
            if not collition:
                continue
            dirction, center, s_rect_L, _, s_rect_W, _, o_rect_L, _, o_rect_W, _ = (
                collition
            )
            overlap = min(s_rect_L + s_rect_W, o_rect_L + o_rect_W) - max(
                s_rect_L, o_rect_L
            )
            if overlap <= 0:
                continue
            push = overlap / 2
            side = -1 if (self.position[0] < other.position[0]) else 1

            self.pending_changes[object_pushback] = {
                "self": self,
                "value": [side * push, 0],
            }
            other.pending_changes[object_pushback] = {
                "self": other,
                "value": [-side * push, 0],
            }

            return {"type": "pushbox"}

    return None


def hitbox_collision(
    game,
    self=BaseActiveObject,
    other=BaseActiveObject,
):
    if (self.hitstop > 0 or other.hitstop > 0) or (self.team == other.team):
        return
    for s_rect in self.boxes["hitbox"].get("rects", []):
        for o_rect in other.boxes["hurtbox"].get("rects", []):
            collition = rect_collide(self, other, s_rect["vec"], o_rect["vec"])
            if not collition:
                continue
            (
                direction,
                center,
            ) = collition[:2]
            if not (
                (other not in self.boxes["hitbox"].get("hitreg", []))
                and (
                    self.type
                    in other.boxes["hurtbox"].get(
                        "vulnerable", ["projectile", "character"]
                    )
                )
                and (other.juggle - self.boxes["hitbox"].get("juggle", 0)) > 0
            ):
                continue

            hitbox = dict(default_hitbox | self.boxes["hitbox"])

            hit_result, ri, ru = hit_logic(game, self, other, hitbox)
            ri += self.combo / 10

            for value in function_dict:
                if hitbox.get(value, None) != None:
                    function_dict[value](
                        self,
                        other=other,
                        value=hitbox[value],
                        hit_result=hit_result,
                        strength=hitbox["strength"],
                        level=hitbox["level"],
                        reaction=hitbox["reaction"],
                        tumble=hitbox["tumble"],
                    )

            object_create_object(
                self,
                [
                    {
                        "dict": "SF3/Sparks",
                        "position": {"vec": list(center)},
                        "rotation": self.rotation,
                        "condition": [hit_result, hitbox["strength"]],
                        "inherit": False,
                    }
                ],
            )
            game.logic_events = game.logic_events + [
                {
                    "tipe": "attack",
                    "result": hit_result,
                    "agents": [
                        {"object": self, "reward": ri},
                        {
                            "object": other,
                            "reward": ru,
                        },
                    ],
                }
            ]
            return


def triggerbox_collision(
    game,
    self=BaseActiveObject,
    other=BaseActiveObject,
):
    for s_rect in self.boxes["triggerbox"].get("rects", []):
        for o_rect in other.boxes["hurtbox"].get("rects", []):
            collition = rect_collide(self, other, s_rect["vec"], o_rect["vec"])
            if not collition:
                continue
            (
                direction,
                center,
            ) = collition[:2]

            if other in self.boxes["triggerbox"].get("hitreg", []):
                continue

            for value in function_dict:
                if self.boxes["triggerbox"].get(value, None) != None:
                    function_dict[value](
                        self,
                        other=other,
                        value=self.boxes["triggerbox"][value],
                        tipe="triggerbox",
                    )
            return {"tipe": "triggerbox"}


box_tipes_func = [
    triggerbox_collision,
    pushbox_collision,
    hitbox_collision,
    environmentbox_collision,
]


def calculate_boxes_collisions(game, *args):
    for func in box_tipes_func:
        for self in game.object_list:
            if self.type in {"projectile", "character", "stage"}:
                for other in game.object_list:
                    if self != other and other.type in {
                        "projectile",
                        "character",
                        "stage",
                    }:
                        func(
                            game,
                            self,
                            other,
                        )
