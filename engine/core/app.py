import pygame

from engine.core.game_loop import GameLoop
from engine.render.renderer import Renderer
from engine.sound.audio_system import AudioSystem
from engine.asset.asset_manager import AssetManager
from engine.input.controller_manager import ControllerManager
from engine.core.event_handler import EventManager
from engine.core.scenes import *


class App:
    def __init__(self, path, **kwargs):
        self.path = path
        self.emu_frame = 0

        self.input = ControllerManager()
        self.loop = GameLoop()
        self.renderer = Renderer(resolution=(640, 400))
        self.audio = AudioSystem()

        self.assets = AssetManager(self.renderer.ctx, self.path + "/Assets")
        self.event = EventManager(app=self)

        self.renderer.shader_programs = self.assets.shaders
        self.renderer.texture_dict = self.assets.images

        self.active = False
        self.scene = FightScene
        self.scene_parameters = {}
        self.scene_sequence = [ModeSelectionScene]

        self.logic_events = []

    def run(self):
        while True:

            params = {
                "input": self.input,
                "loop": self.loop,
                "renderer": self.renderer,
                "audio": self.audio,
                "assets": self.assets,
            } | self.scene_parameters

            self.scene = self.scene_sequence[-1](**params)

            while self.scene.active:

                self.input.update_input()

                self.scene.__loop__()

                self.loop.step(scene=self.scene)

                self.renderer.render(
                    camera=self.scene.camera,
                    light=self.scene.light,
                    shadow=self.scene.shadow,
                    object_list=self.scene.objects,
                    controllers=self.input.devices,
                    show_boxes=self.scene.show_boxes,
                    show_input=self.scene.show_inputs,
                    show_ui=self.scene.show_ui,
                )

                self.audio.update()

                pygame.display.flip()
                self.event.event_handler()
                self.renderer.window.tick()
                self.scene.events.clear()

            self.scene_parameters = self.scene.__dein__()
            if "next_scene" in self.scene_parameters:
                self.scene_sequence.append(self.scene_parameters["next_scene"])

    def fin(self):
        for device in self.input.devices:
            if device.type == "AI":
                device.AI_model.save_model(
                    self.path + "/Assets/model/" + device.target.dict["name"]
                )
        self.active = False
        quit()
        exit()
