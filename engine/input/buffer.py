def list_contains_list(main_list: list, sub_list: list, turn: bool = False) -> bool:
    for sub_item in sub_list:
        item_str = str(sub_item)
        if turn:
            item_str = (
                item_str.replace("right", "__temp__")
                .replace("left", "right")
                .replace("__temp__", "left")
            )
        if item_str[0] == "-":
            if item_str[1:] in main_list:
                return False
        else:
            if item_str not in main_list:
                return False

    return True


def build_state_buffer(self: object, current_condition: set) -> None:
    """Builds a state buffer for the actor (self) by checking the actor's conditions against the conditions specified for each state in the actor's dictionary."""

    current_condition.update(
        [
            "state=" + (self.state_current),
            "hurtbox="
            + (
                self.boxes.get("hurtbox", {}).get("condition", "stand")
                if hasattr(self, "boxes")
                else "stand"
            ),
            "wallbounce="
            + ("true" if hasattr(self, "wallbounce") and self.wallbounce else "false"),
            "defeated="
            + (
                "true"
                if hasattr(self, "meters") and self.meters.get("health", 1) <= 0
                else "false"
            ),
        ]
    )
    for state in self.dict["states"]:
        for condition in self.dict["states"][state].get("condition", []):
            if list_contains_list(
                current_condition, condition, self.rotation[1] == 180
            ):
                self.state_buffer[state] = self.dict["states"][state].get("buffer", 1)
