from engine.constant.entity import *
from engine.gameplay.team import Team
from engine.entity.actor import Actor


def get_actor_per_team(
    team_list: list = [Actor],
    team: Team = Team,
    opposite: bool = True,
    entity_type: EntityType = EntityType.ACTOR,
):
    for tm in team_list:
        if tm.main.type != entity_type:
            continue

        if opposite:
            if tm != team:
                return tm.main
        else:
            if tm == team:
                return tm.main

    return None


def get_actor_per_class(
    object_list: list = [Actor],
    entity_type: EntityType = EntityType.ACTOR,
):
    for actor in object_list:
        if actor.type == entity_type:
            return actor


def get_child_actor_per_class(
    object_list: list = [Actor],
    entity_type: EntityType = EntityType.ACTOR,
    parent=None,
):
    for actor in object_list:
        if actor.type == entity_type and actor.parent == parent:
            return actor
