from typing import Iterable, Union

from engine.constant.entity import *
from engine.entity.actor import Actor


def set_cancel_condition(
    self: Actor, value: Union[str, Iterable[str]] = "", **kwargs
) -> None:
    """Set the cancel conditions for the current frame."""
    if isinstance(value, str):
        value = (value,)

    self.cancel = set(value)


def set_parent_cancel_condition(
    self: Actor, value: Union[str, Iterable[str]] = "", **kwargs
) -> None:
    """Set the cancel conditions for the current frame on the parent."""
    if self.parent == None:
        return

    if isinstance(value, str):
        value = [value]
    self.parent.cancel = value


def set_guard_state(self: Actor, value: list = ["middle", 0], **kwargs) -> None:
    """"""
    pass


def hold_frame_on_hitstop(self: Actor, value: int = 0, **kwargs) -> None:
    """Hold the current frame when the actor is stunned."""
    if self.hitstop > 0:
        self.frame_counter = self.frame_duration - self.hitstop + value


def hold_frame_on_hitstun(self: Actor, value: int = 0, **kwargs) -> None:
    """Hold the current frame when the actor is stunned."""
    if self.hitstun > 0:
        self.frame_counter = self.frame_duration - self.hitstun + value


def add_super_meter(self: Actor, value: int = 0, **kwargs) -> None:
    """Add super meter to the current actor."""
    self.meters["super"] += value


def set_hitstop(self: Actor, value: int = 0, **kwargs) -> None:
    """Sets the hitstop of the current object."""
    self.hitstop = value


def trigger_superstop(self: Actor, value: int = 1, scene=None, **kwargs) -> None:
    """freezes every object in the scene except self for a certain amount of frames."""
    scene.loop.triger_freeze = value
    for object in scene.objects:
        if object != self and object.type in {
            EntityType.BASE,
            EntityType.ACTOR,
            EntityType.PROJECTILE,
        }:
            scene.loop.freeze_actors.add(object)


COMBAT_ACT = {
    "cancel": set_cancel_condition,
    "main_cancel": set_parent_cancel_condition,
    "guard": set_guard_state,
    "hold_on_stun": hold_frame_on_hitstun,
    "bar_gain": add_super_meter,
    "stop": set_hitstop,
    "superstop": trigger_superstop,
}
