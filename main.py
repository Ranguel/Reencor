import os
import string
import json
from pygame import (
    init,
    quit,
    event,
    mixer,
    time,
    display,
    font,
    joystick,
    JOYDEVICEADDED,
)
from pygame.locals import *

from Util.Game_Screens import *
from Util.Common_functions import (
    dummy_json,
    get_object_per_class,
    get_object_per_team,
)
from Util.OpenGL_Renderer import (
    set_mode_opengl,
    load_image_path,
    font_texture,
    Camera,
    Screen,
)
from Util.Input_device import InputDevice, dummy_input
from Util.Interface_objects import Message


current_dir = os.path.dirname(os.path.realpath(__file__))


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))


def get_dictionaries(current_dir):
    object_dict, image_dict, sound_dict = {}, {}, {}
    path = current_dir + "/Assets"

    def get_parent_key(filepath):
        parts = filepath.replace("\\", "/").split("/")
        if len(parts) >= 2:
            folder = parts[-2]
            name = os.path.splitext(parts[-1])[0]
            return f"{folder}/{name}"
        else:
            return os.path.splitext(parts[-1])[0]

    def load_from_path(key, ext, full_path):
        if ext in ["png", "jpg", "jpeg"]:
            try:
                image_dict[key] = load_image_path(full_path)
            except Exception as e:
                print(f"Image load failed for {key}: {e}")
        elif ext in ["wav", "ogg", "mp3"]:
            try:
                sound_dict[key] = mixer.Sound(full_path)
            except Exception as e:
                print(f"Sound load failed for {key}: {e}")
        elif ext in ["json", "xml"]:
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    ob_json = dummy_json | json.load(f)
                    for box in dummy_json["boxes"]:
                        ob_json["boxes"][box] = dummy_json["boxes"][box] | ob_json[
                            "boxes"
                        ].get(box, {})
                    object_dict[key] = ob_json
            except Exception as e:
                print(f"JSON load failed for {key}: {e}")

    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for name in files:
                ext = name.lower().split(".")[-1]
                full_path = os.path.join(root, name)
                key = get_parent_key(os.path.relpath(full_path, path))
                load_from_path(key, ext, full_path)

    font_type = font.Font(current_dir + "/Util/unispace bd.ttf", 60)
    for i in list(string.ascii_letters + string.digits) + [
        "+",
        "-",
        " ",
        ":",
        "_",
        "/",
        "!",
        "?",
        ".",
        ",",
        ";",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
    ]:
        image_dict["font " + i] = font_texture(font_type, i, (200, 200, 200))

    return image_dict, sound_dict, object_dict


class GameObject:
    def __init__(self):
        self.type = "game"

        mixer.pre_init(44100, -16, 1, 1024)
        init()
        mixer.set_num_channels(16)

        self.resolution = (640, 400)
        self.internal_resolution = (1280, 800)
        self.time = time.Clock()
        self.frame_rate = 60

        set_mode_opengl(self.resolution)
        self.camera = Camera(0.1)
        self.screen = Screen(self.internal_resolution)
        display.set_caption("REENCOR")

        self.image_dict, self.sound_dict, self.object_dict = get_dictionaries(
            current_dir
        )
        self.object_list = []

        self.emu_frame = 0
        self.hitstop = 0
        self.camera_focus_point = [0, 0, -400]
        self.superstop, self.camera_path, self.frame, self.pos, self.draw_shake = (
            0,
            {},
            [0, 0],
            [10, 0, 0],
            [0, 0, 0, 0, 0, 0],
        )

        self.show_boxes = False
        self.show_inputs = False

        self.active = True
        self.player_number = 2
        self.selected_characters = "ryu SF3", "ryu SF3"
        self.selected_stage = "trining stage"

        self.Input_device_available()
        self.dummy_input_device = dummy_input

        self.screen_sequence = [
            ModeSelectionScreen,
        ]
        self.current_screen = None
        self.screen_parameters = []

        self.screen_sequence, self.selected_characters, self.selected_stage = (
            [ComboTrialScreen],
            ["SF3/Ryu", "SF3/Ken"],
            ["Reencor/Training"],
        )

        self.record_input = False
        self.reproduce_input = False

        self.active_players = []
        self.active_stages = None

    def Input_device_available(self):
        keyboard_conut = 1
        joystick_count = joystick.get_count()
        for i in range(keyboard_conut):
            self.input_device_list = [InputDevice(self, 1, 1, "keyboard")]
        for i in range(joystick_count):
            self.input_device_list.append(InputDevice(self, 2, i, "joystick"))

    def next_screen(self, screen_sequence: list = [TitleScreen]):
        self.active = False
        self.screen_sequence += screen_sequence

    def screen_manager(self):
        while len(self.screen_sequence):
            self.active = True
            self.current_screen = self.screen_sequence[-1](
                *[self] + self.screen_parameters
            )
            self.screen_parameters = []
            while self.active:
                for dev in self.input_device_list + [self.dummy_input_device]:
                    dev.update()

                self.camera.update(self.camera_focus_point)
                self.current_screen.__loop__()

                self.screen.display()
                display.flip()
                self.event_handler()
                self.time.tick(self.frame_rate)

            self.screen_sequence.pop()
            self.current_screen.__dein__()

            self.hitstop = 0
            self.camera_focus_point = [0, 0, 400]
            self.superstop, self.camera_path, self.frame, self.pos, self.draw_shake = (
                0,
                {},
                [0, 0],
                [10, 0, 0],
                [0, 0, 0, 0, 0, 0],
            )
            self.show_boxes = False
            self.active = True
            self.record_input = False
            self.reproduce_input = False
            self.active_players = []
            self.active_stage = None

    def event_handler(self):
        for individual_event in event.get():
            if individual_event.type == QUIT:
                self.active = False
                quit()
                exit()
            if individual_event.type == KEYDOWN:
                if individual_event.key == K_0:
                    self.active = False
                    exit()
                if individual_event.key == K_9:
                    self.active = False
                    self.screen_manager()
            if individual_event.type == JOYDEVICEADDED:
                i = individual_event.device_index
                self.input_device_list.append(InputDevice(self, 2, i, "joystick"))
                self.active_players[1].inputdevice = self.input_device_list[-1]
                self.input_device_list[-1].active_object = self.active_players[1]
                self.object_list.append(
                    Message(
                        game=self,
                        string="Joystick connected",
                        texture_string=[
                            {"image": "reencor/+", "size": (70, 70)},
                            {"image": "reencor/5", "size": (70, 70)},
                        ],
                        pos=[self.resolution[0] * 0.9, self.resolution[1] * 0.8, -1],
                        background=(0, 0, 0, 126),
                        time=60,
                        kill_on_time=True,
                        allign="left",
                        scale=[0.5, 0.5],
                    )
                )

    def calculate_camera_focus_point(self):
        xpos_list = [active_object.pos[0] for active_object in self.active_players]
        ypos_list = [active_object.pos[1] for active_object in self.active_players]
        self.pos = [
            (sum(xpos_list) / len(xpos_list)),
            (sum(ypos_list) / len(ypos_list)) + self.resolution[1] * 0.6,
            400,
        ]

        camera_limits = self.active_stages[0].dict["camera_focus_point_limit"]
        half_width = self.internal_resolution[0] * 0.5
        half_height = self.internal_resolution[1] * 0.5

        if self.pos[0] - half_width < camera_limits[0][0]:
            self.pos[0] = camera_limits[0][0] + half_width
        elif self.pos[0] + half_width > camera_limits[0][1]:
            self.pos[0] = camera_limits[0][1] - half_width

        if self.pos[1] + half_height > camera_limits[1][0]:
            self.pos[1] = camera_limits[1][0] - half_height
        elif self.pos[1] - half_height < camera_limits[1][1]:
            self.pos[1] = camera_limits[1][1] + half_height

        if self.camera_path:
            path_frame = self.camera_path["path"][self.frame[1]]
            obj = self.camera_path["object"]
            scale = abs(400 / path_frame["pos"][2])
            zoom = (
                abs(self.camera_focus_point[2] / 400)
                if hasattr(self, "camera_focus_point")
                else scale
            )
            cx = path_frame["pos"][0] * obj.face + obj.pos[0]
            cy = path_frame["pos"][1] + obj.pos[1]
            cz = round(scale)
            half_w = self.internal_resolution[0] * 0.5 * zoom
            half_h = self.internal_resolution[1] * 0.5 * zoom
            min_x = self.pos[0] - self.internal_resolution[0] * 0.5 + half_w
            max_x = self.pos[0] + self.internal_resolution[0] * 0.5 - half_w
            min_y = self.pos[1] - self.internal_resolution[1] * 0.5 + half_h
            max_y = self.pos[1] + self.internal_resolution[1] * 0.5 - half_h
            self.camera_focus_point = [
                clamp(cx, min_x, max_x),
                clamp(cy, min_y, max_y),
                cz,
            ]
        else:
            self.camera_focus_point = self.pos

        if self.camera_path:
            self.frame[0] += 1
            if self.frame[0] > self.camera_path["path"][self.frame[1]]["dur"]:
                self.frame = [0, self.frame[1] + 1]
                if self.frame[1] >= len(self.camera_path["path"]):
                    self.camera_path, self.frame = {}, [0, 0]

    def gameplay(self, *args):
        self.emu_frame += 1
        for object in self.object_list:
            object.update(self.camera_focus_point)
        self.hitstop = self.hitstop - 1 if self.hitstop else 0

        for object in self.object_list:
            update_display_shake(object)
        calculate_boxes_collitions(self)
        update_display_shake(self.camera)
        self.calculate_camera_focus_point()

    def display(self, *args):
        for object in self.object_list:
            object.draw(self.screen, self.camera.pos)
            if self.show_boxes:
                draw_boxes(self, object)
        if self.show_inputs:
            for dev in self.input_device_list:
                dev.draw(self.screen, self.camera.pos)


game = GameObject()

game.screen_manager()
