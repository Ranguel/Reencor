from engine.entity.actor import Actor
from engine.gameplay.team import Team

from engine.constant.entity import *
from engine.constant.combat import *
from engine.math.geometry import rect_collide
from engine.gameplay.hit_result import resolve_hit_interaction, evaluate_trigger_event


combat_boxes = {
    "hitbox": "hurtbox",
    "takebox": "grabbox",
    "triggerbox": "hurtbox",
}


def hitbox_collision(
    me: Actor = None,
    you: Actor = None,
    my_team: Team = None,
    your_team: Team = None,
    scene: object = None,
):
    if you in me.hitreg["hitbox"]:
        return

    if me.hitstop > 1 and you.hitstop > 1:
        return

    if me.type not in you.boxes["hurtbox"].get(
        "vulnerable", [EntityType.ACTOR, EntityType.PROJECTILE]
    ):
        return

    if hasattr(you, "juggle") and you.juggle - me.boxes["hitbox"].get("juggle", 0) < 0:
        return

    for s_rect in me.boxes["hitbox"].get("rects", []):
        for o_rect in you.boxes["hurtbox"].get("rects", []):
            collition = rect_collide(me, you, s_rect["vec"], o_rect["vec"])
            if not collition:
                continue

            (
                direction,
                center,
            ) = collition[:2]

            event = resolve_hit_interaction(
                me=me,
                you=you,
                my_team=my_team,
                your_team=your_team,
                scene=scene,
                center=center,
            )
            # ri += my_team.combo / 10

            scene.events.extend(event)

            return


def triggerbox_collision(
    me: Actor = None,
    you: Actor = None,
    my_team: Team = None,
    your_team: Team = None,
    scene: object = None,
):
    if "triggerbox" not in me.boxes or "hurtbox" not in you.boxes:
        return

    if you in me.hitreg["triggerbox"]:
        return

    for s_rect in me.boxes["triggerbox"].get("rects", []):
        for o_rect in you.boxes["hurtbox"].get("rects", []):
            collition = rect_collide(me, you, s_rect["vec"], o_rect["vec"])
            if not collition:
                continue

            (
                direction,
                center,
            ) = collition[:2]

            evaluate_trigger_event(
                me=me,
                you=you,
                my_team=my_team,
                your_team=your_team,
                scene=scene,
                center=center,
            )

            return {"tipe": "triggerbox"}


def grabbox_collision(
    me: Actor = None,
    you: Actor = None,
    my_team: Team = None,
    your_team: Team = None,
    scene: object = None,
):
    pass


combat_boxes_functions = [
    hitbox_collision,
    triggerbox_collision,
    grabbox_collision,
]


def combat_collisions(teams: list[Team] = [], scene: object = None, *args):
    for my_team in teams:
        for your_team in teams:
            if my_team.index == your_team.index:
                continue
            for me in my_team.members:
                for you in your_team.members:
                    for func in combat_boxes_functions:
                        func(
                            me=me,
                            you=you,
                            my_team=my_team,
                            your_team=your_team,
                            scene=scene,
                        )
