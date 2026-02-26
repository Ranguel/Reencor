class InputParser:
    def __init__(self):
        self.interruption = False
        self.last_raw = set()
        self.hold_times = {}
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
            "press": set(),
            "hold": set(),
            "release": set(),
            "dir_transition": (),
            "direction": ("x_neutral", "y_neutral"),
            "numpad": "5",
            "pressed": set(),
        }
        self.plank_window = 2

    def filter_directional_input(self, raw):

        return (
            "left"
            if "left" in raw and "right" not in raw
            else "right" if "right" in raw and "left" not in raw else "x_neutral"
        ), (
            "down"
            if "down" in raw and "up" not in raw
            else "up" if "up" in raw and "down" not in raw else "y_neutral"
        )

    def parse(self, raw):
        self.output["press"] = raw - self.last_raw
        self.output["release"] = self.last_raw - raw
        self.output["hold"] = raw & self.last_raw

        x, y = self.filter_directional_input(raw)

        self.output["dir_transition"] = (
            self.output["direction"][0] + ">" + x,
            self.output["direction"][1] + ">" + y,
        )
        self.output["direction"] = (x, y)
        self.output["numpad"] = self.numpad_lookup.get((x, y), "5")

        self.output["pressed"].clear()

        for b in raw:
            if b in self.output["press"]:
                self.output["pressed"].add(b + "_press")

                for plank in self.hold_times:
                    if 0 < self.hold_times[plank] <= self.plank_window:
                        self.output["pressed"].add(plank + "_press")

            elif b in self.output["release"]:
                self.output["pressed"].add(b + "_release")
            else:
                self.output["pressed"].add(b + "_hold")

            self.hold_times[b] = self.hold_times.get(b, 0) + 1

        for b in self.output["release"]:
            self.hold_times[b] = 0

        for punch in range(len(raw & self.punches)):
            self.output["pressed"].add("P" * (punch + 1) + "_press")
        for kick in range(len(raw & self.kicks)):
            self.output["pressed"].add("K" * (kick + 1) + "_press")

        if raw != self.last_raw:
            self.interruption = True
        else:
            self.interruption = False

        self.last_raw = set(raw)

        return self.output
