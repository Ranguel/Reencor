import numpy
import math
from typing import Union

from engine.gameplay.team import Team
from engine.entity.actor import Actor
from engine.constant.ui import *
from engine.constant.combat import *
from engine.math.vector import normalize_length, rotate_vector
from engine.action.draw import trigger_render_shake
from engine.action.state import find_next_state, get_target_state_by_condition


def register_target(self: Actor, other: Actor, box_type="hitbox", **kwargs) -> None:
    """Registers a successful hit by adding the defender (other) to the hitreg set attacker (self) of the specified box type.
    This function is used to track which targets have been hit by a particular hitbox during combat resolution, allowing for effects like hitstop and damage to be applied only once per target per hitbox activation.
    """

    self.hitreg[box_type].add(other)


def apply_meter_on_hit(
    self: Actor,
    other: Actor,
    my_team: Team = None,
    value: dict = {},
    hit_result: HitResult = HitResult.HIT,
    **kwargs
) -> None:
    """Apply meter gain or loss to the attacker (self) and defender (other) during combat resolution based on the hit result.
    Meter changes can be determined by hit result and specified in the value dictionary for different hit results.
    This function updates the meters of both the attacker and defender based on the hit result, which can be used to create effects like building super meter for the attacker upon landing hits or losing meter for the defender upon being hit.
    """

    output = {}

    scaling = my_team.damage_scaling
    for meter, results in value.items():
        if hit_result.name.lower() not in results:
            continue
        for target_name, amount in results[hit_result.name.lower()].items():
            adjusted_amount = math.ceil(amount * scaling)
            target = self if target_name == "self" else other
            if meter in target.meters:
                target.meters[meter] += adjusted_amount
                output[meter] = adjusted_amount
                # target.pending_changes[meter] = target.meters[meter] + adjusted_amount

    return output


def apply_hitstun(
    self: Actor,
    other: Actor,
    my_team=None,
    value: Union[int, dict] = 0,
    hit_result: HitResult = HitResult.HIT,
    strength: AttackStrength = AttackStrength.MEDIUM,
    **kwargs
) -> None:
    """Apply hitstun to the defender (other) when hit during combat resolution.
    Hitstun duration can be determined by hit result and attack strength.
    This function updates the defender's pending changes with a hitstun value that can be used to trigger a hitstun state transition and associated effects when the defender is hit.
    """

    output = {}

    if not other.hitstun:
        # Reset combo scaling on first hit
        my_team.damage_scaling = 1
        my_team.combo = 0
        # Add unique identifier for the attack to the combo list to prevent multiple scaling from the same attack
        my_team.combo_list.append(str(self.id) + str(self.attack_id))
    else:
        if (str(self.id) + str(self.attack_id)) not in my_team.combo_list:
            attack_values = ATTACK_SCALING.get(
                strength, ATTACK_SCALING[AttackStrength.MEDIUM]
            )
            my_team.damage_scaling = my_team.damage_scaling = max(
                my_team.damage_scaling - attack_values["scaling"],
                attack_values["min"],
            )

        my_team.combo += 1
        # Add unique identifier for the attack to the combo list to prevent multiple scaling from the same attack
        my_team.combo_list.append(str(self.id) + str(self.attack_id))

        # Update team combo label with shake effect
        for label in my_team.labels:
            if label.subtype == UISubtype.COMBO:
                label.show = True
                label.show_timer = 60
                label.string_update("COMBO " + str(my_team.combo + 1))
                label.draw_shake.trigger(
                    strength=0.04,
                    direction=(1, 0),
                    duration=20,
                    damping=0.3,
                )

    if hit_result.name.lower() not in value:
        value[hit_result.name.lower()] = value[next(iter(value))]

    if value == int and hit_result in [HitResult.HIT, HitResult.BLOCK]:
        other.pending_changes["hitstun"] = value
    else:
        other.pending_changes["hitstun"] = value.get(hit_result.name.lower(), 10)

    output["hitstun"] = other.pending_changes["hitstun"]

    return output


def apply_hitstop(
    self: Actor,
    other: Actor,
    value: Union[int, dict] = 0,
    hit_result: HitResult = HitResult.HIT,
    **kwargs
) -> None:
    """Apply hitstop to both the attacker (self) and defender (other) during combat resolution.
    Hitstop duration can be determined by hit result and can have different values for self and other.
    This function updates the pending changes of both the attacker and defender with hitstop values that can be used to trigger hitstop effects, such as freezing the animation and input of both characters for a certain duration based on the hit result.
    """

    output = {}

    DEFAULT_PARRY = {"self": 16, "other": 12}

    value = value or {}

    # Case 1: Simple integer
    if isinstance(value, int):
        if hit_result in (HitResult.HIT, HitResult.BLOCK):
            hs_self = hs_other = value
        else:  # parry
            hs_self, hs_other = DEFAULT_PARRY["self"], DEFAULT_PARRY["other"]

    # Case 2: Dict
    else:
        # If result not specified, fallback to first available key
        if hit_result.name.lower() not in value:
            first_key = next(iter(value))
            value[hit_result.name.lower()] = value[first_key]

        v = value[hit_result.name.lower()]

        # Case: value[hit_result] = int
        if isinstance(v, int):
            hs_self = hs_other = v

        # Case: value[hit_result] = dict
        else:
            hs_self = v.get(
                "self", DEFAULT_PARRY["self"] if hit_result == HitResult.PARRY else 0
            )
            hs_other = v.get(
                "other", DEFAULT_PARRY["other"] if hit_result == HitResult.PARRY else 0
            )

    self.pending_changes["hitstop"] = hs_self
    other.pending_changes["hitstop"] = hs_other

    output["hitstop"] = hs_other

    # self.pending_changes["frame_counter"] = 0
    # self.pending_changes["frame_duration"] = hs_self
    # other.pending_changes["frame_counter"] = 0
    # other.pending_changes["frame_duration"] = hs_other

    target = self if hit_result == HitResult.PARRY else other
    strength_val = 0.01 * (hs_other if hit_result != HitResult.PARRY else 1)
    duration = hs_self if hit_result == HitResult.PARRY else hs_other

    direction = (
        (1, 0)
        if hit_result == HitResult.PARRY
        else (other.pending_changes.get("speed", [1, 1]))
    )

    trigger_render_shake(
        target,
        {
            "strength": strength_val,
            "direction": direction,
            "duration": duration,
            "damping": 1,
        },
    )

    if hit_result == HitResult.PARRY:
        self.pending_changes[trigger_render_shake] = {
            "self": self,
            "value": {"shake": [0, 10, 10], "target": "camera"},
        }

    return output


def apply_knockback(
    self: Actor,
    other: Actor,
    value: dict = {},
    hit_result: HitResult = HitResult.HIT,
    tumble: bool = False,
    **kwargs
) -> None:
    """Apply knockback to the defender (other) during combat resolution based on the hit result and contact state.
    Knockback can be a simple vector or determined by hit result and whether the defender is grounded or airborne.
    Knockback can also have a type that modifies its behavior, such as "inherit" to inherit the attacker's speed and direction.
    This function updates the defender's pending changes with a speed vector that can be used to apply knockback movement to the defender upon being hit, as well as handling special cases like blocking or parrying that may modify the knockback applied.
    """

    output = {}

    contact = "grounded" if other.grounded else "airborne"
    knockback = [0, 0]
    knockback_type = ""
    data = value.get(hit_result.name.lower())

    if data is None:
        if hit_result == HitResult.BLOCK:
            data = value.get("hit")
        elif hit_result == HitResult.HIT:
            data = value.get("block")
    if data is None:
        data = value if "vec" in value else None
    if isinstance(data, dict):
        if "vec" in data:
            knockback = data["vec"]
            knockback_type = data.get("type", "")
        elif contact in data:
            state = data[contact]
            knockback = state.get("vec", [0, 0])
            knockback_type = state.get("type", "")
    if hit_result == HitResult.BLOCK:
        knockback = [knockback[0], 0]
    elif hit_result == HitResult.PARRY:
        knockback = [0, 0]
        knockback_type = ""

    if knockback_type == "inherit":
        knockback = normalize_length(knockback) + rotate_vector(
            self.rotation, self.speed
        )

    other.pending_changes["speed"] = (
        rotate_vector(self.rotation, normalize_length(knockback))
        + numpy.array(
            [
                0,
                (
                    0.2
                    if (other.meters.get("health", 1) <= 0 and knockback[1] == 0)
                    else 0
                ),
                0,
            ],
            dtype=numpy.float32,
        )
    ) * self.scale

    output["knockback"] = other.pending_changes["speed"]

    if (
        tumble.get("grounded" if other.grounded else "airborne", "no")
        == hit_result.name.lower()
        or other.meters.get("health", 1) <= 0
    ) and other.grounded:
        other.pending_changes["grounded"], other.pending_changes["position"] = (
            False,
            other.position + numpy.array([0, 0.1, 0]) * self.scale,
        )

    return output


def apply_damage(
    self: Actor,
    other: Actor,
    my_team: Team = None,
    value: Union[int, dict] = 0,
    hit_result: HitResult = HitResult.HIT,
    **kwargs
) -> None:
    """Apply damage to the defender (other) during combat resolution based on the hit result.
    Damage can be a simple integer or determined by hit result.
    This function also updates the attacker's team damage scaling and combo count based on the hit result.
    """
    output = {}

    if isinstance(value, int):
        damage = value * my_team.damage_scaling

    elif hit_result.name.lower() in value:
        damage = value[hit_result.name.lower()] * my_team.damage_scaling

    other.meters["health"] -= damage
    output["damage"] = damage
    my_team.last_damage = damage

    if my_team.combo > 0:
        my_team.combo_damage += damage
    else:
        my_team.combo_damage = my_team.last_damage

    return output

    if isinstance(value, int):
        other.pending_changes["meters"] = {
            "health": other.meters.get("health", 0)
            - (value * self.parent.damage_scaling)
        }
        return

    if hit_result.name.lower() in value:
        other.pending_changes["meters"] = {
            "health": other.meters.get("health", 0)
            - (value[hit_result.name.lower()] * self.parent.damage_scaling)
        }


def apply_hit_reaction(
    self: Actor,
    other: Actor,
    value: AttackLevel = AttackLevel.MID,
    hit_result: HitResult = HitResult.HIT,
    strength: AttackStrength = AttackStrength.MEDIUM,
    reaction: AttackReaction = AttackReaction.NONE,
    tumble: bool = False,
    **kwargs
) -> None:
    """Apply hit reaction to the defender (other) during combat resolution based on the hit result and attack strength.
    Hit reaction can be determined by hit result and can have different values for different hit results.
    This function updates the defender's condition set with the hit result, hit level based on attack strength, and other relevant information that can be used for state transitions and other effects.
    """

    other.condition.update(
        [
            hit_result.name.lower(),
            "level=" + str(value),
            "strength=" + str(strength),
            "reaction=" + str(reaction),
            (
                "tumble=true"
                if tumble.get("grounded" if other.grounded else "airborne", "no")
                == hit_result.name.lower()
                else ""
            ),
        ]
    )
    if other.meters.get("health", 1) <= 0:
        other.condition.update(["reaction=hook", "tumble=true"])

    (
        other.pending_changes[get_target_state_by_condition],
        self.pending_changes["current_condition"],
        other.pending_changes["rotation"],
    ) = (
        {
            "self": self,
            "value": {
                "condition": other.condition,
                "force": True,
            },
            "other": other,
        },
        self.condition | {"did_" + hit_result.name.lower()},
        numpy.array(
            [
                other.rotation[0],
                180 if (self.rotation[1] == 0) else 0,
                other.rotation[2],
            ],
            dtype=numpy.float32,
        ),
    )


def update_state_on_hit(
    self: Actor, value: dict = {}, hit_result: HitResult = HitResult.HIT, **kwargs
) -> None:
    """Update the state of the attacker (self) during combat resolution based on the hit result.
    The new state can be determined by hit result and specified in the value dictionary for different hit results.
    This function uses the find_next_state function to determine the appropriate state transition based on the attacker's current condition set after being updated with the hit result information.
    """

    state = find_next_state(
        self, state_buffer={value.get(hit_result.name.lower(), "none"): 1}, force=True
    )


def apply_position_on_hit(
    self: Actor,
    other: Actor,
    value: dict = {},
    hit_result: HitResult = HitResult.HIT,
    **kwargs
) -> None:
    """Apply positional adjustment to the defender (other) during combat resolution based on the hit result.
    The positional adjustment can be determined by hit result and specified in the value dictionary for different hit results.
    This function updates the defender's position by adding a vector specified in the value dictionary for the corresponding hit result, which can be used to create effects like sliding or launching the defender upon being hit.
    """

    if hit_result.name.lower() in value:
        other.pending_changes["position"] = (
            self.position
            + rotate_vector(
                self.rotation, normalize_length(value[hit_result.name.lower()]["vec"])
            )
            * self.scale
        )


def apply_juggle_limit(
    self: Actor,
    other: Actor,
    value: int = 0,
    hit_result: HitResult = HitResult.HIT,
    tumble: bool = False,
    **kwargs
) -> None:
    """Apply juggle limit to the defender (other) during combat resolution based on the hit result and contact state.
    Juggle limit can be determined by hit result and whether the defender is grounded or airborne.
    This function updates the defender's juggle count, which can be used to limit the number of times a defender can be juggled in the air before being forced to the ground.
    """

    if (
        (not other.grounded)
        or (
            other.grounded
            and tumble.get("grounded" if other.grounded else "airborne", "no")
            == HitResult.HIT.name.lower()
        )
    ) and hit_result == HitResult.HIT:
        other.pending_changes["juggle"] = other.juggle - value


def apply_wallbounce(self: Actor, other: Actor, value: bool = True, **kwargs) -> None:
    """Apply wallbounce state to the defender (other) during combat resolution based on the hit result and contact state.
    This function updates the defender's pending changes with a wallbounce flag that can be used to trigger a wallbounce state transition and associated effects when the defender collides with a wall after being hit.
    """

    other.pending_changes["wallbounce"] = value


HIT_ACT = {
    "other_get_state": get_target_state_by_condition,
    "hitreg": register_target,
    "knockback": apply_knockback,
    "hitstop": apply_hitstop,
    "hitstun": apply_hitstun,
    "damage": apply_damage,
    "hit_meter": apply_meter_on_hit,
    "level": apply_hit_reaction,
    "state_on_hit": update_state_on_hit,
    "pos_on_hit": apply_position_on_hit,
    "juggle": apply_juggle_limit,
    "wallbounce": apply_wallbounce,
}
