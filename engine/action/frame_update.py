from engine.action.draw import DRAW_ACT
from engine.action.sound import SOUND_ACT
from engine.action.motion import MOTION_ACT
from engine.action.box import BOXES_ACT
from engine.action.actor import COMBAT_ACT
from engine.action.combat import HIT_ACT
from engine.action.state import STATE_ACT
from engine.action.object import OBJECT_ACT


def set_frame_duration(self, value=1, **kwargs):
    """The duration of the substate in frames. 'dur': duration"""
    self.frame_counter, self.frame_duration = 0, value


def object_remove_box_key(self: object, value: str = "", **kwargs):
    self.boxes[value[0]].pop(value[1], None)


def apply_pending_changes(self: object = None, scene=None, **kwargs):
    for key, value in self.pending_changes.items():
        if callable(key):
            key(**value | {"scene": scene})
        else:
            setattr(self, key, value)

    self.pending_changes.clear()


REGISTRY_ACT = {
    "remove_box_key": object_remove_box_key,
}


FRAME_ACTIONS = (
    REGISTRY_ACT
    | STATE_ACT
    | HIT_ACT
    | DRAW_ACT
    | SOUND_ACT
    | MOTION_ACT
    | BOXES_ACT
    | COMBAT_ACT
    | OBJECT_ACT
)


def apply_frame_data(self, scene, action_dict=FRAME_ACTIONS, **kwargs):
    """Applies frame data to the object."""
    self.ignore_stop = False
    self.hold_on_stun = False
    self.cancel = set([None])

    for value in action_dict:
        if self.frame_data.get(value, None) != None:
            action_dict[value](scene=scene, self=self, value=self.frame_data[value])

    set_frame_duration(self, value=self.frame_data.get("dur", 1))
