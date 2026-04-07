from engine.constant.commands import COMMAND_SEQUENCE


class CommandDetector:
    def __init__(self, commands=COMMAND_SEQUENCE):
        self.commands = commands
        self.state = {
            cmd["name"]: {"index": 0, "timer": 0, "numpad": ""} for cmd in commands
        }
        self.active = set()

    def update(self, parsed_input, interruption=1):
        for cmd in self.commands:
            name = cmd["name"]
            expected_sequence = cmd["sequence"]
            timeout = cmd.get("timeout", 12)
            buffer = cmd.get("buffer", 6)
            state = self.state[name]

            if state["timer"] > 0 and not (
                state["index"] == 1 and state["numpad"] == parsed_input["numpad"]
            ):
                state["timer"] -= 1

            if state["timer"] == 0:
                if name in self.active:
                    self.active.discard(name)
                if state["index"] > 0:
                    state["index"] = 0
                    state["numpad"] = "0"

            expected = expected_sequence[state["index"]]

            if (
                interruption
                and self._match_step(expected, parsed_input)
                and state["numpad"] != parsed_input["numpad"]
            ):
                state["index"] += 1
                state["timer"] = timeout
                state["numpad"] = parsed_input["numpad"]
                if state["index"] == len(expected_sequence):
                    self.active.add(name)
                    state["index"] = 0
                    state["timer"] = buffer
                    state["numpad"] = "0"

        return self.active

    def _match_step(self, expected, parsed):
        for token in expected:
            if token.startswith("-"):
                if (
                    token[1:] in parsed["pressed"]
                    or token[1:] in parsed["direction"]
                    or token[1:] in parsed["dir_transition"]
                ):
                    return False
            else:
                if (
                    token not in parsed["direction"]
                    and token not in parsed["pressed"]
                    and token not in parsed["dir_transition"]
                ):
                    return False
        return True
