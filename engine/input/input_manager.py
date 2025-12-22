from pygame._sdl2 import controller
from engine.input.input_device import BaseInputDevice, Keyboard


def get_available_input_device(app):
    controller.init()
    app.input_device_list = []

    app.input_device_list.append(Keyboard(app=app, side=False))

    app.dummy_input_device = BaseInputDevice()
    app.input_device_list.append(app.dummy_input_device)
