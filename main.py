import os
from pygame import init, quit, event, mixer, time, display, joystick
from pygame.locals import *

from Util.Game_Screens import *
from Util.Object_functions import get_dictionaries, get_object_per_class, get_object_per_team
from Util.OpenGL_Renderer import set_mode_opengl, Camera, Screen
from Util.Input_device import InputDevice

current_dir = os.path.dirname(os.path.realpath(__file__))


def Input_available_device():
    keyboard_conut = 1
    joystick_count = joystick.get_count()
    devices = [InputDevice(1, 1, 'keyboard', 1), InputDevice(2, 2, 'none', 1)]
    try:
        devices[1] = InputDevice(2, 0, 'joystick', 1)
    except:
        pass

    return devices


class GameObject():
    def __init__(self):
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
        display.set_caption('REENCOR')

        self.image_dict, self.sound_dict, self.object_dict = get_dictionaries(current_dir)

        self.tipe = 'game'

        self.emu_frame = 0
        self.hitstop = 0
        self.camera_focus_point = [0, 0, -400]
        self.superstop, self.camera_path, self.frame, self.pos, self.draw_shake = 0, {}, [
            0, 0], [10, 0, 0], [0, 0, 0, 0, 0, 0]

        self.show_boxes = False
        self.show_inputs = False

        self.active = True
        self.selected_characters = 'ryu SF3', 'ryu SF3'
        self.selected_stage = 'trining stage'

        self.input_device_list = Input_available_device()
        self.dummy_input_device = InputDevice(1, 1, 'none', 1)

        self.screen_sequence = [ModeSelectionScreen,
                                ]
        #self.screen_sequence = [DebuggingScreen]

        self.current_screen = None

        self.record_input = False
        self.reproduce_input = False

        self.active_player_1 = None
        self.active_player_2 = None
        self.active_stage = None

        self.object_list = []

    def next_screen(self, screen_sequence: list = [TitleScreen]):
        self.active = False
        self.screen_sequence += screen_sequence

    def screen_manager(self):
        while len(self.screen_sequence):
            self.active = True
            self.current_screen = self.screen_sequence[-1](self)
            while self.active:
                for dev in self.input_device_list+[self.dummy_input_device]:
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
            self.camera_focus_point = [0, 0, -200]
            self.superstop, self.camera_path, self.frame, self.pos, self.draw_shake = 0, {}, [
                0, 0], [10, 0, 0], [0, 0, 0, 0, 0, 0]
            self.show_boxes = False
            self.active = True
            self.record_input = False
            self.reproduce_input = False
            self.active_player_1 = None
            self.active_player_2 = None
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

    def calculate_camera_focus_point(self):
        self.pos = [(self.active_player_1.pos[0]+self.active_player_2.pos[0]) /
                    2, -self.resolution[1]*0.6+(self.active_player_1.pos[1]+self.active_player_2.pos[1])/2, -400]

        if self.pos[0]-self.internal_resolution[0]*0.5 < object_dict[self.active_stage.name]['camera_focus_point_limit'][0][0]:
            self.pos[0] = object_dict[self.active_stage.name]['camera_focus_point_limit'][0][0] + \
                self.internal_resolution[0]*0.5
        if self.pos[0]+self.internal_resolution[0]*0.5 > object_dict[self.active_stage.name]['camera_focus_point_limit'][0][1]:
            self.pos[0] = object_dict[self.active_stage.name]['camera_focus_point_limit'][0][1] - \
                self.internal_resolution[0]*0.5
        if self.pos[1]+self.internal_resolution[1]*0.5 > object_dict[self.active_stage.name]['camera_focus_point_limit'][1][0]:
            self.pos[1] = object_dict[self.active_stage.name]['camera_focus_point_limit'][1][0] - \
                self.internal_resolution[1]*0.5
        if self.pos[1]-self.internal_resolution[1]*0.5 < object_dict[self.active_stage.name]['camera_focus_point_limit'][1][1]:
            self.pos[1] = object_dict[self.active_stage.name]['camera_focus_point_limit'][1][1] + \
                self.internal_resolution[1]*0.5

        if self.camera_path:
            self.camera_focus_point = [self.camera_path['path'][self.frame[1]]['pos'][0]*self.camera_path['object'].face+self.camera_path['object'].pos[0],
                                       self.camera_path['path'][self.frame[1]]['pos'][1]+self.camera_path['object'].pos[1], round(-400/self.camera_path['path'][self.frame[1]]['pos'][2])]
            if self.camera_focus_point[0]+self.internal_resolution[0]*abs(self.camera_focus_point[2]/400)*0.5 > self.pos[0]+self.internal_resolution[0]*0.5:
                self.camera_focus_point[0] = self.pos[0]+self.internal_resolution[0]*0.5-(
                    self.internal_resolution[0]*abs(self.camera_focus_point[2]/400)*0.5)
            if self.camera_focus_point[0]-self.internal_resolution[0]*abs(self.camera_focus_point[2]/400)*0.5 < self.pos[0]-self.internal_resolution[0]*0.5:
                self.camera_focus_point[0] = self.pos[0]-self.internal_resolution[0]*0.5+(
                    self.internal_resolution[0]*abs(self.camera_focus_point[2]/400)*0.5)
            if self.camera_focus_point[1]+self.internal_resolution[1]*abs(self.camera_focus_point[2]/400)*0.5 > self.pos[1]+self.internal_resolution[1]*0.5:
                self.camera_focus_point[1] = self.pos[1]+self.internal_resolution[1]*0.5-(
                    self.internal_resolution[1]*abs(self.camera_focus_point[2]/400)*0.5)
            if self.camera_focus_point[1]-self.internal_resolution[1]*abs(self.camera_focus_point[2]/400)*0.5 < self.pos[1]-self.internal_resolution[1]*0.5:
                self.camera_focus_point[1] = self.pos[1]-self.internal_resolution[1]*0.5+(
                    self.internal_resolution[1]*abs(self.camera_focus_point[2]/400)*0.5)
        else:
            self.camera_focus_point = self.pos

        if self.camera_path:
            self.frame[0] += 1
            if self.frame[0] > self.camera_path['path'][self.frame[1]]['dur']:
                self.frame = [0, self.frame[1]+1]
                if self.frame[1] >= len(self.camera_path['path']):
                    self.camera_path, self.frame = {}, [0, 0]

    def gameplay(self, *args):
        self.emu_frame += 1
        for object in self.object_list:
            object.update(self.camera_focus_point)

        if self.active_player_1 == None:
            self.active_player_1 = get_object_per_team(self.object_list, 1, False)
        if self.active_player_2 == None:
            self.active_player_2 = get_object_per_team(self.object_list, 2, False)
        if self.active_stage == None:
            self.active_stage = get_object_per_class(self.object_list, 'StageActiveObject')
            # GL_set_light(object_dict[self.active_stage.name].get(
            # 	'light', [-1, 1, -2, 0]))
            # GL_set_ambient(object_dict[self.active_stage.name].get(
            # 	'ambient', [.9, .9, .9, 1]))

        self.hitstop = self.hitstop-1 if self.hitstop else 0

        calculate_boxes_collitions(self)

        for object in self.object_list:
            update_display_shake(object)

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
