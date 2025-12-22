import pygame
from pygame._sdl2 import controller
from engine.gameplay.common_functions import get_object_per_team

from engine.input.mapping import keyboard_mapping, controller_mapping, AI_mapping
from engine.input.input_parser import InputParser
from engine.input.commnad_detector import CommandDetector


class BaseInputDevice:
    def __init__(
        self,
        app: object = None,
        side: int = 0,
    ):
        self.type = "none"
        self.app, self.side, self.mapping = app, side, ()

        self.input_raw = set()
        self.button_display_list = []
        self.render_list = []

        self.input_interruption = False
        self.target = None

        self.parser = InputParser()
        self.detector = CommandDetector()

    def get_input(self):
        return {"x_neutral", "y_neutral"}

    def update(self, *args):
        if self.target is None and self.app is not None:
            self.target = get_object_per_team(self.app.object_list, self.side)
            self.target.input_device = self

        raw = self.get_input()
        parsed = self.parser.parse(raw=raw)
        command = self.detector.update(parsed_input=parsed)

        if self.parser.interruption:

            if len(self.button_display_list) > 20:
                self.button_display_list.pop(0)
            self.button_display_list.append(parsed["buttons"])

            if self.target is not None:
                self.target.input_interruption = True

        if self.target is not None:
            self.target.input = parsed["buttons"] | set(parsed["direction"])
            self.target.command = command

    def render(self, renderer, *args):
        if not self.input_interruption:
            renderer.draw_queue.extend(self.render_list)
            return

        self._build_draw_command()

        renderer.draw_queue.extend(self.render_list)

    def _build_draw_command(self):
        self.render_list = []
        for y, input_set in enumerate(self.button_display_list):
            x = 0
            for input in input_set:
                key = "reencor/" + input
                if key not in self.app.image_dict:
                    continue
                image = self.app.image_dict[key]
                aspect = image[1][0] / image[1][1]
                render_cmd = {
                    "color_texture": image[0],
                    "position": (-0.95 + x * 0.04, -0.9 + y * 0.06),
                    "size": (0.03, 0.06),
                    "rotation": 0,
                    "keep_aspect": True,
                    "texture_aspect": aspect,
                    "flip": [False, False],
                    "tint": (1, 1, 1, 1),
                    "side": (False if self.target is None else self.target.side),
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
