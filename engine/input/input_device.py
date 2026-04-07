import pygame
from pygame._sdl2 import controller

from engine.constant.ui import *
from engine.input.mapping import keyboard_mapping, controller_mapping, AI_mapping
from engine.input.input_parser import InputParser
from engine.input.commnad_detector import CommandDetector
from engine.gameplay.object_query import get_actor_per_team

inputs_shown = {
    "A_press",
    "B_press",
    "X_press",
    "Y_press",
    "R1_press",
    "R2_press",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
}


class BaseInputDevice:
    def __init__(
        self,
        side: ScreenSide = ScreenSide.LEFT,
    ):
        self.type = "none"
        self.side, self.mapping = side, ()

        self.input_raw = set()
        self.button_display_list = [set()]
        self.render_list = []

        self.interruption = False
        self.target = []

        self.parser = InputParser()
        self.detector = CommandDetector()

    def get_input(self):
        return {"x_neutral", "y_neutral"}

    def update(self, **kwargs):
        raw = self.get_input()
        parsed = self.parser.parse(raw=raw)
        command = self.detector.update(
            parsed_input=parsed, interruption=self.parser.interruption
        )

        if self.parser.interruption:
            if len(self.button_display_list) > 20:
                self.button_display_list.pop(0)
            self.button_display_list.append(parsed["pressed"] | set(parsed["numpad"]))

            self.interruption = True

            for object in self.target:
                object.input_interruption = True

        for object in self.target:
            object.input.update(parsed["pressed"] | set(parsed["direction"]))
            object.command.update(command)

    def render(self, **kwargs):
        if not self.interruption:
            return self.render_list

        self._build_draw_command()

        return self.render_list

    def _build_draw_command(self):
        self.render_list = []

        for y, input_set in enumerate(self.button_display_list):

            if input_set.isdisjoint(inputs_shown):
                continue

            x = 0

            for input in input_set:

                if input not in inputs_shown:
                    continue

                color_texture = "icon/" + input
                texture_aspect = color_texture

                render_cmd = {
                    "color_texture": color_texture,
                    "position": (-0.95 + x * 0.04, -0.9 + y * 0.06),
                    "size": (0.03, 0.06),
                    "rotation": 0,
                    "keep_aspect": True,
                    "texture_aspect": texture_aspect,
                    "flip": [False, False],
                    "tint": (1, 1, 1, 1),
                    "side": self.side == ScreenSide.RIGHT,
                    "program": "ui",
                }

                self.render_list.append(render_cmd)

                x += 1


class Keyboard(BaseInputDevice):
    def __init__(self, **kwarg):
        super().__init__(**kwarg)
        self.type = "keyboard"
        self.mapping = keyboard_mapping

    def get_input(self):
        raw = set()
        pressed = pygame.key.get_pressed()
        for k in self.mapping:
            if pressed[k["act"]]:
                raw.update(k["input"])
        return raw


class Controller(BaseInputDevice):
    def __init__(self, index, **kwarg):
        super().__init__(**kwarg)
        self.type = "controller"
        self.mapping = controller_mapping
        self.controller = controller.Controller(index)

    def get_input(self):
        raw = set()
        for input in controller_mapping:
            if input["tipe"] == "axis":
                if (
                    self.controller.get_axis(input["act"]) * input["dir"]
                    > input["deadzone"] * 32767
                ):
                    raw.update(input["input"])
            if input["tipe"] == "button":
                if self.controller.get_button(input["act"]):
                    raw.update(input["input"])
        return raw


class ArtificialIntelligence(BaseInputDevice):
    def __init__(self, **kwarg):
        super().__init__(**kwarg)
        self.type = "AI"
        self.mapping = AI_mapping
        # import Util.AI_Controller as ai_controller
        # self.AI_model = ai_controller.AI_Controller(output_size=len(AI_mapping))

    def get_input(self):
        raw = set()
        return raw

    def give_reward(self, reward=0, label: str = ""):
        if self.AI_model:
            self.AI_model.give_reward(reward=reward, force_training=True, label=label)


class ComputerVision(BaseInputDevice):
    def __init__(self, **kwarg):
        super().__init__(**kwarg)
        self.type = "CV"
        self.mapping = keyboard_mapping

    def get_input(self):
        # Each item must have this format: "CV=" + movement. Example: "CV=Standing Jab"
        raw = set()
        return raw
