import pygame
from engine.input.input_device import Controller

WINDOW_FLAGS = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE


class EventManager:
    def __init__(self, app):
        self.app = app
        self.pygame_events = []
        self.game_events = []

    def event_handler(self):
        self.pygame_events = []
        for event in pygame.event.get():
            self.handle_quit(event)
            self.handle_keyboard(event)
            self.handle_window_resize(event)
            self.handle_joystick(event)

    def handle_quit(self, event=pygame.event):
        if event.type == pygame.QUIT:
            self.app.fin()

    def handle_keyboard(self, event=pygame.event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_0:
            self.app.fin()

        elif event.key == pygame.K_9:
            self.app.vsync = not self.app.vsync

    def handle_window_resize(self, event=pygame.event):
        if event.type != pygame.VIDEORESIZE:
            return

        width, height = event.w, event.h

        self.app.renderer.resolution = (width, height)
        self.app.renderer.aspect_ratio = width / height
        self.app.renderer.aspect_ratio_inv = height / width
        self.app.renderer.ctx.viewport = (0, 0, width, height)

    def handle_joystick(self, event=pygame.event):
        if event.type != pygame.JOYDEVICEADDED:
            return

        device_index = event.device_index

        device = Controller(app=self.app, index=device_index, side=True)

        self.app.controllers.append(device)
        self.app.active_players[1].inputdevice = device
        device.active_object = self.app.active_players[1]

    def handle_logic_events(self):
        for event in self.app.logic_events:
            self.process_logic_event(event)
        self.app.logic_events.clear()

    def process_logic_event(self, event):
        if event["tipe"] == "attack":
            for agent in event["agents"]:
                device = agent["object"].input_device
                if device:
                    parent = agent["object"].parent
                    target = parent if parent else agent["object"]
                    reward = agent["reward"]
                    # device.give_reward(reward, label="hitbox " + str(event["result"]))
