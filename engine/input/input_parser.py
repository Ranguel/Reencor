class InputParser:
    def __init__(self):
        self.interruption = False
        self.last_raw = set()
        self.hold_times = {}
        self.directional = {"left", "right", "up", "down"}
        self.numpad_lookup = {
            ("left", "down"): "1",
            ("x_neutral", "down"): "2",
            ("right", "down"): "3",
            ("left", "y_neutral"): "4",
            ("x_neutral", "y_neutral"): "5",
            ("right", "y_neutral"): "6",
            ("left", "up"): "7",
            ("x_neutral", "up"): "8",
            ("right", "up"): "9",
        }
        self.kicks = {"A", "B", "R2"}
        self.punches = {"X", "Y", "R1"}
        self.output = {
            "raw": set(),
            "press": set(),
            "hold": set(),
            "release": set(),
            "direction": None,
            "numpad": None,
            "buttons": set(),
        }

    def parse(self, raw):
        self.output["raw"] = set(raw)
        self.output["press"] = raw - self.last_raw
        self.output["release"] = self.last_raw - raw
        self.output["hold"] = raw & self.last_raw

        for b in raw:
            self.hold_times[b] = self.hold_times.get(b, 0) + 1
        for b in self.last_raw - raw:
            self.hold_times[b] = 0

        x = (
            "left"
            if "left" in raw and "right" not in raw
            else "right" if "right" in raw and "left" not in raw else "x_neutral"
        )

        y = (
            "down"
            if "down" in raw and "up" not in raw
            else "up" if "up" in raw and "down" not in raw else "y_neutral"
        )
        self.output["direction"] = (x, y)
        self.output["numpad"] = self.numpad_lookup.get((x, y), "5")

        self.output["buttons"] = set()
        for b in raw:
            if b not in self.directional:
                if b in self.output["press"]:
                    self.output["buttons"].add(b + "_press")
                elif b in self.output["release"]:
                    self.output["buttons"].add(b + "_release")
                else:
                    self.output["buttons"].add(b + "_hold")
        for punch in range(len(raw & self.punches)):
            self.output["buttons"].add("P" * (punch + 1) + "_press")
        for kick in range(len(raw & self.kicks)):
            self.output["buttons"].add("K" * (kick + 1) + "_press")

        if raw != self.last_raw:
            self.interruption = True
        else:
            self.interruption = False

        self.last_raw = set(raw)

        return self.output
