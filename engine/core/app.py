import os
import pygame

from engine.core.game_loop import GameLoop
from engine.graphics.renderer import Renderer
from engine.assets.asset_manager import AssetManager
from engine.input.input_manager import get_available_input_device
from engine.core.event_handler import EventManager
from engine.core.scenes import IncialScreen, DebuggingScreen


class App:
    def __init__(self, path, **kwargs):
        self.path = path
        self.resolution = (640, 400)
        self.aspect_ratio = self.resolution[0] / self.resolution[1]
        self.emu_frame = 0

        self.renderer = Renderer(resolution=(640, 400))
        self.assets = AssetManager(self.renderer.ctx, self.path + "/Assets")
        self.event = EventManager(app=self)

        self.renderer.shader_programs = self.assets.shaders

        self.image_dict, self.sound_dict, self.object_dict, self.shader_programs = (
            self.assets.images,
            self.assets.sounds,
            self.assets.objects,
            self.assets.shaders,
        )

        self.object_list = []

        self.input_device_list = []
        get_available_input_device(self)

        self.show_boxes = False
        self.show_inputs = False

        self.active = False
        self.player_number = 2
        self.selected_characters = "ryu SF3", "ryu SF3"
        self.selected_stage = "trining stage"

        self.active_players = []
        self.active_stages = None

        self.screen_sequence = [
            IncialScreen,
        ]
        self.current_screen = None
        self.screen_parameters = []

        self.screen_sequence, self.selected_characters, self.selected_stage = (
            [DebuggingScreen],
            ["SF3/Ryu", "SF3/Ryu"],
            ["Reencor/Training"],
        )

        self.logic_events = []

    def run(self):
        loop = GameLoop(self)

        while len(self.screen_sequence):
            self.active = True
            self.current_screen = self.screen_sequence[-1](
                *[self] + self.screen_parameters
            )
            self.screen_parameters = []

            while self.active:

                loop.step()
                self.current_screen.__loop__()

                self.renderer.render(
                    object_list=self.object_list,
                    input_device_list=self.input_device_list,
                    draw_boxes=self.show_boxes,
                    draw_input=self.show_inputs,
                )
                pygame.display.flip()
                self.event.event_handler()
                self.renderer.window.tick()

    def fin(self):
        for device in self.input_device_list:
            if device.type == "AI":
                device.AI_model.save_model(
                    self.path + "/Assets/model/" + device.target.dict["name"]
                )
        self.active = False
        quit()
        exit()
