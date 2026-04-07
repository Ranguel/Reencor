import numpy

from engine.constant.entity import *
from engine.constant.entity import *
from engine.math.probability import weighted_choice
from engine.input.buffer import build_state_buffer


def find_next_state(
    self: object, state_buffer: dict | None = None, force: bool = False
) -> str:
    """ "Find the next state for the actor (self) by checking the provided state buffer against the actor's conditions and other relevant factors such as grounded state, cancel conditions, and meter costs."""

    state_buffer = state_buffer or {}
    states = self.dict["states"]
    current_state = self.state_current

    for state_name in states:

        if state_name not in state_buffer:
            continue

        state = states[state_name]

        grounded_ok = (
            self.grounded == state.get("grounded", self.grounded)
            if hasattr(self, "grounded")
            else True
        )
        if not grounded_ok:
            continue

        frames_finished = (
            self.frame_index >= self.frame_total
            and self.frame_counter >= self.frame_duration
        )

        cancel_ok = True

        if hasattr(self, "cancel"):
            cancel_list = set(state.get("cancel", []))
            # cancel_list = set(["neutral","interrupt","normal","special","EX"]) #turbo cancel
            no_cancel_states = set(state.get("no_cancel_states", []))
            neutral_cancel = frames_finished and "neutral" in cancel_list
            input_cancel = (
                self.hitstop == 0 if hasattr(self, "hitstop") else True
            ) and (
                not cancel_list.isdisjoint(
                    self.cancel
                    # | set(
                    #     ["kara"] if hasattr(self, "kara") and 4 > self.kara > 0 else []
                    # )
                )
            )
            cancel_ok = (
                input_cancel and current_state not in no_cancel_states
            ) or neutral_cancel

            ### fix

        super_cost = state.get("bar_use", 0)
        gauge_ok = (
            self.meters.get("super", 0) >= super_cost
            if hasattr(self, "meters")
            else True
        )

        if not force and not (cancel_ok and gauge_ok):
            continue
        if super_cost:
            self.meters["super"] -= super_cost

        self.state_interruption = True
        self.state_current = state_name
        if hasattr(self, "attack_id"):
            self.attack_id += 1
        self.state_buffer.clear()
        self.state_data = state["framedata"]

        self.boxes = dict(self.dict["defaults"]["boxes"])
        self.kara = 6

        self.frame_index = 0
        self.frame_total = len(self.state_data)
        self.frame_counter = 0
        self.frame_duration = 0
        self.frame_repeat = 0

        self.acceleration = numpy.zeros(3, dtype=numpy.float32)
        self.gravity = numpy.array(self.dict["gravity"], dtype=numpy.float32)
        self.con_speed = numpy.zeros(3, dtype=numpy.float32)

        if (
            self.type == EntityType.ACTOR
            and self.input_device
            and state.get("reward", 0)
        ):
            for box_type in self.hitreg:
                self.hitreg[box_type].clear()

            cancel_type = set(self.cancel) & cancel_list

            bonus = (
                0.02
                if "interrupt" in cancel_type
                else (
                    0.04
                    if "normal" in cancel_type
                    else 0.08 if "special" in cancel_type else 0.0
                )
            )

            reward = float(state["reward"] + bonus)
            # self.input_device.give_reward(reward, f"new state {state_name}")

        return state_name

    return ""


def repeat_from_frame(self: object, value: int, **kwargs) -> None:
    """Set the frame data to repeat from a specific frame index for a certain number of repeats.
    This can be used to create looping animations or effects within a state by specifying a frame index to loop back to and the number of times to repeat that loop.
    """

    if self.frame_repeat < value[1] or value[1] == -1:
        self.frame_data = self.state_data[value[0]]
        self.frame_index = value[0] + 1

    if self.frame_repeat == value[1]:
        self.frame_data = self.state_data[self.frame_index]
        self.frame_index += 1

    self.frame_repeat += 1


def get_state_by_condition(self: object, value: dict, **kwargs) -> str:
    """Updates the current state of the actor (self) by searching through a state buffer built from the actor's conditions."""

    build_state_buffer(
        self,
        current_condition=self.input
        | set(self.condition)
        | set(value.get("condition", [])),
    )
    state = find_next_state(
        self, state_buffer=self.state_buffer, force=value.get("force", False)
    )

    if state:
        self.frame_data = self.state_data[0]
        return state

    return ""


def get_target_state_by_condition(
    self: object,
    value: dict,
    other: object,
    **kwargs,
) -> str:
    """Updates the current state of the target (other) by searching through a state buffer built from the target's conditions."""

    build_state_buffer(
        other,
        current_condition=other.input
        | other.condition
        | set(value.get("condition", [])),
    )
    state = find_next_state(
        other, state_buffer=other.state_buffer, force=value.get("force", False)
    )

    if state:
        self.frame_data = self.state_data[0]
        return state

    return ""


def select_random_state(self: object, value: dict, **kwargs) -> str:
    """Selects a random state from the provided options based on their associated chances and updates the current state accordingly."""

    random_state = weighted_choice(value)
    state = find_next_state(self, state_buffer={random_state: 2}, force=True)

    if state:
        self.frame_data = self.state_data[0]
        return state

    return ""


def trigger_state(self: object, value: str, **kwargs) -> str:
    """Triggers a specific state by name, bypassing the usual condition checks and directly setting the current state to the specified value."""

    state = find_next_state(self, state_buffer={value: 1}, force=True)

    if state:
        self.frame_data = self.state_data[0]
        return state

    return ""


STATE_ACT = {
    "frame_repeat": repeat_from_frame,
    "get_state": get_state_by_condition,
    "other_get_state": get_target_state_by_condition,
    "trigg_state": trigger_state,
    "random_state": select_random_state,
}
