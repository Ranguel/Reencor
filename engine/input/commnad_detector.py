commands = {
    "QC": (("down", "-right"), ("down",), ("right",)),
    "DP": (("right",), ("down", "-right"), ("down",)),
    "DQC": (
        ("down", "-right"),
        ("down",),
        ("down", "-right"),
        ("down",),
        ("right",),
    ),
    "Doble_tap": (
        ("right_press", "-down", "-up"),
        ("x_neutral", "-down", "-up"),
        ("right_press", "-down", "-up"),
    ),
    "Down_Up_tap": (("down",), ("-down", "-up"), ("up",)),
}

command_sequence_list = (
    {
        "name": "QC_right",
        "sequence": (("down", "-right"), ("down",), ("right",)),
        "coinsidence": 0,
        "timer": 0,
        "last_directional_input": [],
    },
    {
        "name": "QC_left",
        "sequence": (["down", "-left"], ("down",), ("left",)),
        "coinsidence": 0,
        "timer": 0,
        "last_directional_input": [],
    },
    {
        "name": "DP_right",
        "sequence": (("right",), ("down", "-right"), ("down",)),
        "coinsidence": 0,
        "timer": 0,
        "last_directional_input": [],
    },
    {
        "name": "DP_left",
        "sequence": (("left",), ("down", "-left"), ("down",)),
        "coinsidence": 0,
        "timer": 0,
        "last_directional_input": [],
    },
    {
        "name": "DQC_right",
        "sequence": (
            ("down", "-right"),
            ("down",),
            ("down", "-right"),
            ("down",),
            ("right",),
        ),
        "coinsidence": 0,
        "timer": 0,
        "timeout": 14,
        "last_directional_input": [],
    },
    {
        "name": "DQC_left",
        "sequence": (
            ("down", "-left"),
            ("down",),
            ("down", "-left"),
            ("down",),
            ("left",),
        ),
        "coinsidence": 0,
        "timer": 0,
        "timeout": 14,
        "last_directional_input": [],
    },
    {
        "name": "Doble_tap_right",
        "sequence": (
            ("right_press", "-down", "-up"),
            ("x_neutral", "-down", "-up"),
            ("right_press", "-down", "-up"),
        ),
        "coinsidence": 0,
        "timer": 0,
        "timeout": 8,
        "last_directional_input": [],
        "buffer": 5,
    },
    {
        "name": "Doble_tap_left",
        "sequence": (
            ("left_press", "-down", "-up"),
            ("x_neutral", "-down", "-up"),
            ("left_press", "-down", "-up"),
        ),
        "coinsidence": 0,
        "timer": 0,
        "timeout": 8,
        "last_directional_input": [],
        "buffer": 5,
    },
    {
        "name": "down_up_tap",
        "sequence": (("down",), ("-down", "-up"), ("up",)),
        "coinsidence": 0,
        "timer": 0,
        "last_directional_input": [],
        "buffer": 5,
    },
)


class CommandDetector:
    def __init__(self, commands=command_sequence_list):
        self.commands = commands
        self.state = {
            cmd["name"]: {"index": 0, "timer": 0, "last_dir": 0} for cmd in commands
        }
        self.active = set()

    def update(self, parsed_input):
        for cmd in self.commands:
            name = cmd["name"]
            expected_sequence = cmd["sequence"]
            timeout = cmd.get("timeout", 9)
            buffer = cmd.get("buffer", 6)
            st = self.state[name]

            if st["timer"] > 0:
                st["timer"] -= 1

            if st["timer"] == 0:
                if name in self.active:
                    self.active.discard(name)
                if st["index"] > 0:
                    st["index"] = 0
                    st["last_dir"] = 0

            expected = expected_sequence[st["index"]]

            if (
                self._match_step(expected, parsed_input)
                and st["last_dir"] != parsed_input["numpad"]
            ):
                st["index"] += 1
                st["timer"] = timeout
                st["last_dir"] = parsed_input["numpad"]
                if st["index"] == len(expected_sequence):
                    self.active.add(name)
                    st["index"] = 0
                    st["timer"] = 20

        return self.active

    def _match_step(self, expected, parsed):
        for token in expected:
            if token.startswith("-"):
                if (
                    token[1:] in parsed["buttons"]
                    or token[1:] == parsed["direction"][0]
                ):
                    return False
            else:
                if token in {"down", "up", "left", "right"}:
                    if token not in parsed["direction"]:
                        return False
                else:
                    if token not in parsed["buttons"]:
                        return False
        return True
