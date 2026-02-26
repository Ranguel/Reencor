from engine.math.vector import normalize_length, rotate_vector
from engine.constant.physics import *
from engine.constant.entity import *
from engine.gameplay.team import Team
from engine.entity.actor import Actor
from engine.entity.projectile import Projectile
from engine.entity.visual import Visual


def create_projectile(self: Actor = None, value=None, scene=None, **kwargs):

    for obj in value:
        space = obj.get("space", "local")
        prnt = self if obj.get("parent", False) else None
        base_dict = scene.prefabs.get(obj.get("dict", "none"))

        scl = normalize_length(obj.get("scale", [1, 1]))
        rot = normalize_length(obj.get("rotation", [0, 0]))
        pos = normalize_length(obj.get("position", {}).get("vec", [0, 0]))

        if space == "local":
            scl = self.scale * scl
            rot = self.rotation + rot
            pos = self.position + rotate_vector(self.rotation, pos) * scl

        new = Projectile(
            dict=base_dict,
            position=pos,
            rotation=rot,
            scale=scl,
            state=obj.get("state", "none"),
            condition=obj.get("condition", ["x_neutral", "y_neutral"]),
            palette=obj.get("palette", 0),
            parent=prnt,
        )

        new.team = self.team

        self.team.members.append(new)
        scene.objects.append(new)


def create_visual_effect(self: Actor = None, value=None, scene=None, **kwargs):

    for obj in value:

        base_dict = scene.prefabs.get(obj.get("dict", "none"))

        scl = normalize_length(obj.get("scale", [1, 1]))
        rot = normalize_length(obj.get("rotation", [0, 0]))
        pos = normalize_length(obj.get("position", {}).get("vec", [0, 0]))

        space = (
            PositionSpace.LOCAL if obj.get("space") == "local" else PositionSpace.GLOBAL
        )
        prnt = (
            self if (space is PositionSpace.LOCAL or obj.get("parent", False)) else None
        )
        spawn = obj.get("spawn", "local") if space is PositionSpace.GLOBAL else None

        if spawn == "local":
            scl = self.scale * scl
            rot = self.rotation + rot
            pos = self.position + rotate_vector(self.rotation, pos) * scl

        new = Visual(
            dict=base_dict,
            position=pos,
            rotation=rot,
            scale=scl,
            state=obj.get("state", "none"),
            condition=obj.get("condition", ["x_neutral", "y_neutral"]),
            palette=obj.get("palette", 0),
            parent=prnt,
            space=space,
        )

        scene.objects.append(new)
        if prnt == self:
            self.children.append(new)


def actor_child_kill(self: Actor = None, state_interruption=False, **kwargs):
    """Kill the object instantly."""
    for child in self.children:
        if hasattr(child, "life_time"):
            if state_interruption:
                if self.state_interruption and child.space == PositionSpace.LOCAL:
                    child.life_time = 0
            else:
                child.life_time = 0


def actor_kill(self: Actor = None, **kwargs):
    """Kill the object instantly."""
    if hasattr(self, "life_time"):
        self.life_time = 0


OBJECT_ACT = {
    "create_projectile": create_projectile,
    "create_visual_effect": create_visual_effect,
    "kill": actor_kill,
}
