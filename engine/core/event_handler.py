import pygame
from engine.input.input_device import Controller

WINDOW_FLAGS = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE


class EventManager:
    def __init__(self, app):
        self.app = app
        self.events = []

    def event_handler(self):
        self.events = []
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

        # self.app.update_camera_projection()
        # self.app.resize_framebuffers(width, height)

    def handle_joystick(self, event=pygame.event):
        if event.type != pygame.JOYDEVICEADDED:
            return

        device_index = event.device_index

        device = Controller(app=self.app, index=device_index, side=True)

        self.app.input_device_list.append(device)
        self.app.active_players[1].inputdevice = device
        device.active_object = self.app.active_players[1]
