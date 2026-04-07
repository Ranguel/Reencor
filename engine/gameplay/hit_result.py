from engine.entity.actor import Actor
from engine.gameplay.team import Team
from engine.constant.combat import *
from engine.action.frame_update import FRAME_ACTIONS, apply_pending_changes
from engine.action.object import create_visual_effect

DEF_HITBOX = {
    "hitstun": {"hit": 40, "block": 38},
    "hitstop": {"hit": 9, "block": 9, "parry": {"self": 16, "other": 14}},
    "juggle": 2,
    "knockback": {"hit": {"grounded": [0, 0]}},
    "strength": AttackStrength.MEDIUM,
    "level": AttackLevel.MID,
    "reaction": AttackReaction.NONE,
    "tumble": {"grounded": "no", "airborne": "no"},
}

DEF_TRIGGERBOX = {
    "effect": None,
    # "level": AttackLevel.MID,
}

DEF_BOX = {
    "hitbox": DEF_HITBOX,
    "triggerbox": DEF_TRIGGERBOX,
}


def get_AttackStrength(s: str):
    if s == "light" or s == 1:
        return AttackStrength.LIGHT
    elif s == "heavy" or s == 3:
        return AttackStrength.HEAVY
    elif s == "special" or s == 4:
        return AttackStrength.SPECIAL
    elif s == "super" or s == 5:
        return AttackStrength.SUPER
    else:
        return AttackStrength.MEDIUM


def get_AttackLevel(s: str):
    if s == "low" or s == 1:
        return AttackLevel.LOW
    elif s == "high" or s == 3:
        return AttackLevel.HIGH
    else:
        return AttackLevel.MID


def get_AttackReaction(s: str):
    if s == "jaw" or s == 1:
        return AttackReaction.JAW
    elif s == "uppercut" or s == 2:
        return AttackReaction.UPPERCUT
    elif s == "solarplex" or s == 3:
        return AttackReaction.SOLARPLEX
    elif s == "body" or s == 4:
        return AttackReaction.BODY
    elif s == "hook" or s == 5:
        return AttackReaction.HOOK
    elif s == "trip" or s == 6:
        return AttackReaction.TRIP
    elif s == "turn" or s == 7:
        return AttackReaction.TURN
    elif s == "overhead" or s == 8:
        return AttackReaction.OVERHEAD
    else:
        return AttackReaction.NONE


def hit_block_parry(
    me: Actor,
    you: Actor,
    level: AttackLevel = AttackLevel.MID,
):
    hit_result, ri, ru = (HitResult.HIT, 0.2, -0.15)

    if (
        set(you.cancel).intersection(("neutral", "interruption", "blocking"))
        and you.grounded
        and (
            ("left" in you.input and you.rotation[1] == 0)
            or ("right" in you.input and you.rotation[1] == 180)
        )
    ) or you.guard == "block":
        if level in ("high", "middle") and "down" not in you.input:
            hit_result, ri, ru = HitResult.BLOCK, 0.25, 0.2
        else:
            ri, ru = 0.3, -0.2
        if level in ("low", "middle") and "down" in you.input:
            hit_result, ri, ru = HitResult.BLOCK, 0.25, 0.2
        else:
            ri, ru = 0.3, -0.2

    if (
        set(you.cancel).intersection(("neutral", "interruption", "blocking", "parry"))
        and you.grounded
        and you.guard[1] >= 16
    ) or you.guard == "parry":
        if (
            level in ("high", "middle")
            and (
                ("left" in you.input and you.rotation[1] == 180)
                or ("right" in you.input and you.rotation[1] == 0)
            )
            and "y_neutral" in you.input
        ):
            hit_result, ri, ru = HitResult.PARRY, 0.1, 0.4
            you.guard[1] = 0
        else:
            ri, ru = 0.35, -0.25
        if (
            level in ("low", "middle")
            and "x_neutral" in you.input
            and "down" in you.input
        ):
            hit_result, ri, ru = HitResult.PARRY, 0.1, 0.4
            you.guard[1] = 0
        else:
            ri, ru = 0.35, -0.25

    # hit_result, ri, ru = HitResult.PARRY, 0.1, 0.4

    return hit_result, ri, ru


def resolve_hit_interaction(
    me: Actor,
    you: Actor,
    my_team: Team,
    your_team: Team,
    center: list = [0, 0, 0],
    scene: object = None,
):
    data = dict(DEF_BOX["hitbox"] | me.boxes["hitbox"])

    hit_result, ri, ru = hit_block_parry(me, you, data["level"])

    strength = get_AttackStrength(data["strength"])
    level = get_AttackLevel(data["level"])
    reaction = get_AttackReaction(data["reaction"])

    events = [
        {"resolution": hit_result},
        {"my reward": ri},
        {"your reward": ru},
    ]

    for value in FRAME_ACTIONS:
        if data.get(value, None) != None:
            action = FRAME_ACTIONS[value](
                me,
                other=you,
                my_team=my_team,
                your_team=your_team,
                value=data[value],
                hit_result=hit_result,
                strength=strength,
                level=level,
                reaction=reaction,
                tumble=data["tumble"],
                box_type="hitbox",
                scene=scene,
            )
            if action != None and action and isinstance(action, dict):
                events.append(action)

    create_visual_effect(
        me,
        [
            {
                "dict": "SF3/Sparks",
                "position": {"vec": list(center)},
                "rotation": me.rotation,
                "condition": (hit_result.name.lower(), str(strength)),
                "spawn": "global",
            }
        ],
        scene=scene,
    )

    apply_pending_changes(me, scene=scene)
    apply_pending_changes(you, scene=scene)

    return events


def evaluate_trigger_event(
    me: Actor,
    you: Actor,
    my_team: Team,
    your_team: Team,
    center: list = [0, 0, 0],
    scene: object = None,
):
    data = dict(DEF_BOX["triggerbox"] | me.boxes["triggerbox"])

    hit_result, ri, ru = hit_block_parry(me, you)

    for value in FRAME_ACTIONS:
        if data.get(value, None) != None:
            FRAME_ACTIONS[value](
                me,
                other=you,
                my_team=my_team,
                your_team=your_team,
                value=data[value],
                hit_result=hit_result,
                box_type="triggerbox",
                scene=scene,
            )

    apply_pending_changes(me)
    apply_pending_changes(you)

    return hit_result, ri, ru
