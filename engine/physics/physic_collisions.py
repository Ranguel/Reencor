import numpy

from engine.constant.entity import *
from engine.math.vector import normalize_length
from engine.math.geometry import rect_collide
from engine.action.motion import apply_pushback
from engine.action.draw import trigger_render_shake
from engine.action.state import get_state_by_condition
from engine.action.frame_update import apply_frame_data
from engine.gameplay.team import Team
from engine.entity.base import Base
from engine.entity.actor import Actor


physics_boxes = {
    "environmentbox": "environmentbox",
    "pushbox": "pushbox",
}


def environmentbox_collision(me: Actor, you: Actor, scene=None):
    touch_ground = False

    if you.type is not EntityType.BASE:
        return touch_ground
    if "environmentbox" not in me.boxes or "environmentbox" not in you.boxes:
        return touch_ground
    if me.dict["physics_type"] == "static":
        return touch_ground

    for s_rect in me.boxes["environmentbox"].get("rects", []):
        for o_rect in you.boxes["environmentbox"].get("rects", []):
            colision = rect_collide(me, you, s_rect["vec"], o_rect["vec"])
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
                if not me.grounded and not me.grabed and me.hitstop == 0:
                    me.grounded = True
                    me.juggle = 100
                    me.hitstun = 0
                    me.wallbounce = False
                    me.air_time = 0
                    me.condition.update(["landed"])

                    if me.boxes["hurtbox"].get("condition") == "tumble":
                        trigger_render_shake(
                            me,
                            value={
                                "strength": 0.2,
                                "direction": [0, 1],
                                "target": "camera",
                            },
                            scene=scene,
                        )
                    get_state_by_condition(me, value={"force": True})
                    apply_frame_data(self=me, scene=scene)
                    me.frame_interruption = False
                    me.frame_counter = 1
                    me.frame_index = 1

                if not me.hitstop:
                    friction = (
                        me.boxes["environmentbox"].get("grounded_friction", 0.7)
                        if not me.hitstun
                        else 0.85
                    )
                    me.speed[0] *= friction
                me.position[1] = o_rect_D + o_rect_H - s_rect["vec"][1] - 0.001
                me.speed[1] = max(me.speed[1], 0)

            # ───────────── CEILING ─────────────
            elif direction == "down":
                me.position[1] = o_rect_D - s_rect_H - s_rect["vec"][1]
                me.condition.update(["hit_ceiling"])

            # ───────────── WALLS ─────────────
            elif direction in ("left", "right"):
                me.condition.update(["hit_wall"])

                if direction == "right":
                    me.position[0] = o_rect_L - s_rect_W / 2
                else:
                    me.position[0] = o_rect_L + o_rect_W + s_rect_W / 2

                if me.wallbounce and not me.grounded:
                    me.rotation[1] = 0 if direction == "right" else 180
                    me.speed = (
                        [-0.12, 0.25, 0] if direction == "right" else [0.12, 0.25, 0]
                    ) * me.scale
                    me.hitstop = 8

                    trigger_render_shake(
                        me,
                        value={
                            "strength": 0.2,
                            "direction": [1, 0],
                            "target": "camera",
                        },
                        scene=scene,
                    )
                    get_state_by_condition(me, value={"force": True})
                    apply_frame_data(self=me, scene=scene)
                    me.frame_interruption = False
                    me.frame_counter = 1
                    me.frame_index = 1
                    me.wallbounce = False

    return touch_ground


def pushbox_collision(me: Actor, you: Actor, scene=None):
    if "pushbox" not in me.boxes or "pushbox" not in you.boxes:
        return
    for s_rect in me.boxes["pushbox"].get("rects", []):
        for o_rect in you.boxes["pushbox"].get("rects", []):
            collition = rect_collide(me, you, s_rect["vec"], o_rect["vec"])
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
            side = -1 if (me.position[0] < you.position[0]) else 1

            me.pending_changes[apply_pushback] = {
                "self": me,
                "value": [side * push, 0],
            }
            you.pending_changes[apply_pushback] = {
                "self": you,
                "value": [-side * push, 0],
            }

            return {"type": "pushbox"}

    return None


physics_boxes_functions = [
    pushbox_collision,
    environmentbox_collision,
]


def physics_collisions(
    teams: list = [Team, Team], bases: list = [Base, Base], scene=None, *args
):

    for my_team in teams:
        for your_team in teams:
            if my_team.index == your_team.index:
                continue
            for me in my_team.members:
                for you in your_team.members:
                    pushbox_collision(me=me, you=you, scene=scene)

                touch_ground = False

                for base in bases:

                    if (
                        environmentbox_collision(me=me, you=base, scene=scene)
                        and not touch_ground
                    ):
                        touch_ground = True

                if not touch_ground:
                    if me.grounded:
                        me.input_interruption = 1
                    me.grounded = False
                    me.speed *= numpy.array(
                        normalize_length(
                            me.boxes["environmentbox"].get(
                                "airborne_friction", [1, 1, 1]
                            )
                        ),
                        dtype=numpy.float32,
                    )

                    if hasattr(me, "air_time"):
                        me.air_time += 1
