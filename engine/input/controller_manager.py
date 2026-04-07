from pygame._sdl2 import controller

from engine.constant.ui import *
from engine.input.input_device import Keyboard, Controller


class ControllerManager:
    def __init__(self):
        self.devices = [Keyboard]
        self.get_controllers()

    def get_controllers(self):
        controller.init()
        self.devices = [Keyboard(side=ScreenSide.LEFT)]
        side = ScreenSide.RIGHT
        for i in range(controller.get_count()):
            if controller.is_controller(i):
                self.devices.append(Controller(side=side, index=i))
                side = ScreenSide.LEFT if side == ScreenSide.RIGHT else ScreenSide.RIGHT

    def update_input(self):
        for device in self.devices:
            device.update()
