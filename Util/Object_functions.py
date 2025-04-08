import os
import json

import random
import math
import string

import zipfile
from io import BytesIO

from Util.OpenGL_Renderer import *

object_list = []
everything_list = []

color = [(255, 0, 0, 200), (0, 0, 255, 200), (0, 255, 0, 200), (255, 255, 0, 200),
         (255, 0, 255, 200), (0, 255, 255, 200), (255, 255, 255, 200), (0, 0, 0, 200)]

colors = {'hurtbox': (20, 20, 255, 255), 'hitbox': (255, 20, 20, 255), 'takebox': (20, 255, 255, 255), 'grabbox': (
    20, 255, 20, 255), 'pushbox': (255, 0, 255, 255), 'triggerbox': (255, 128, 0, 255), 'boundingbox': (255, 255, 255, 255)}

default_substate = {'dur': 1}

default_hitbox = {'damage': (0, 0), 'gain': (0, 0), 'stamina': (0, 0), 'hitstun': (
    0, 0), 'hitstop': 10, 'juggle': 1, 'knockback': {"grounded": [0, 0]}, 'hittipe': ['medium', 'middle']}

attack_tipe_value = {'parry': {'scaling': 10, 'min_scaling': 0}, 'block': {'scaling': 10, 'min_scaling': 10}, 'critical': {'scaling': 10, 'min_scaling': 40}, 'super': {'scaling': 10, 'min_scaling': 36}, 'special': {
    'scaling': 10, 'min_scaling': 16}, 'heavy': {'scaling': 10, 'min_scaling': 14}, 'medium': {'scaling': 9, 'min_scaling': 12}, 'light': {'scaling': 8, 'min_scaling': 10}, 'no_match': {'scaling': 8, 'min_scaling': 40}}

dummy_json = {
    "tipe": "proyectile",
    "palette": [],
    "scale": [1, 1],
    "gravity": 0,
    "mass": 1,
    "music": "",
    "terminal_velocity": 1,
    "gauges": {},
    "boxes": {"hurtbox": {"boxes": []}, "hitbox": {"boxes": [], "hitset": 1}, "takebox": {"boxes": []}, "grabbox": {"boxes": []}, "pushbox": {"boxes": []}, "triggerbox": {"boxes": []}, "boundingbox": {"boxes": [[-75, 0, 150, 310]], "friction": 0.7}},
    "offset": [0, 0],
    "timekill": False,
    "trials": [],
    "moveset": {
    }
}


def nomatch(*args): pass


def gradient_color(value, max_value, color1, color2):
    if len(color1) == 3:
        color1 += [255]
    if len(color1) == 3:
        color2 += [255]
    if max_value == 0:
        return (0, 0, 0)
    value = max(0, min(value, max_value))
    t = value / max_value
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    a = int(color1[3] + (color2[3] - color1[3]) * t)
    return (r, g, b, a)


def palette_swap(image, palette):
    new = pygame.PixelArray(image)
    for color in palette:
        new.replace(tuple(color[0]), tuple(color[1]), .01)
    del new
    return image


def normalizar(valor, min_valor, max_valor): return (
    valor - min_valor) / (max_valor - min_valor)


def reescale(values, escale): return [round(value*escale) for value in values]


def RoundSign(n): return int(1) if n > 0 else int(-1) if n < 0 else int(0)


def weighted_choice(options):
    values = list(options.keys())
    probabilities = [options[key]['chance'] for key in values]
    return random.choices(values, weights=probabilities, k=1)[0]


def get_object_per_team(team: int = 0, opposite: bool = True, class_name='CharacterActiveObject'):
    for self in object_list:
        if self.__class__.__name__ == class_name:
            if (self.team != team and opposite) or (self.team == team and opposite == False):
                return self


def get_object_per_class(class_name: str = 'CharacterActiveObject'):
    for self in object_list:
        if self.__class__.__name__ == class_name:
            return self


def get_object_per_class_ev(class_name: str = 'CharacterActiveObject'):
    for self in everything_list:
        if self.__class__.__name__ == class_name:
            return self


object_dict, image_dict, sound_dict = {}, {}, {}


def update_display_shake(self):
    if self.draw_shake[2] == self.draw_shake[5]:
        self.draw_shake = [0, 0, 0, 0, 0, 0]
    if self.draw_shake[5]:
        factor = math.sin((self.draw_shake[2] % 3) / 3 * math.pi * 2) * abs(
            self.draw_shake[5] - self.draw_shake[2]) / self.draw_shake[5]
        self.draw_shake = [self.draw_shake[3] * factor, self.draw_shake[4] * factor,
                           self.draw_shake[2]+1, self.draw_shake[3], self.draw_shake[4], self.draw_shake[5]]


def normalize_vector(x, y, base=1):
    magnitude = math.sqrt(x**2 + y**2)  # Calcular la magnitud del vector
    if magnitude == 0:
        return [0, 1 * base]  # Caso especial cuando el vector es (0,0)
    # Normalización estándar
    return [x / magnitude * base, y / magnitude * base]


def unzip_if_needed(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith('.zip'):
                zip_path = os.path.join(root, file)
                folder_name = os.path.splitext(file)[0]

                folder_exists = False
                for sub_root, dirs, _ in os.walk(path):
                    if folder_name in dirs:
                        folder_exists = True
                        break

                if not folder_exists:
                    extract_path = os.path.join(root, folder_name)
                    print(f"Descomprimiendo: {zip_path} -> {extract_path}")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)


def get_dictionaries(current_dir):
    path = current_dir + '/Assets'

    unzip_if_needed(path)

    def get_parent_key(filepath):
        parts = filepath.replace('\\', '/').split('/')
        if len(parts) >= 2:
            folder = parts[-2]
            name = os.path.splitext(parts[-1])[0]
            return f"{folder}/{name}"
        else:
            return os.path.splitext(parts[-1])[0]

    def load_from_file(key, ext, data):
        if ext in ['png', 'jpg', 'jpeg']:
            try:
                image_dict[key] = load_image_bites(data)
            except:
                pass
        elif ext in ['wav', 'ogg', 'mp3']:
            try:
                sound_dict[key] = pygame.mixer.Sound(BytesIO(data))
            except:
                pass
        elif ext in ['json', 'xml']:
            try:
                ob_json = dummy_json | json.loads(data.decode('utf-8'))
                for box in dummy_json['boxes']:
                    ob_json["boxes"][box] = dummy_json['boxes'][box] | ob_json["boxes"].get(box, {
                    })
                object_dict[key] = ob_json
            except:
                pass

    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for name in files:
                ext = name.lower().split('.')[-1]
                full_path = os.path.join(root, name)
                key = get_parent_key(os.path.relpath(full_path, path))
                with open(full_path, 'rb') as f:
                    load_from_file(key, ext, f.read())

    font = pygame.font.Font(current_dir + '/Util/unispace bd.ttf', 38)
    for i in list(string.ascii_letters + string.digits) + ['+', '-', ' ', ':', '_']:
        image_dict['font ' + i] = font_texture(font, i, (126, 126, 126))

    return image_dict, sound_dict, object_dict


def string_size(string=str, scale=(1, 1)):
    offset_turn = 0
    for i in string:
        offset_turn += image_dict['font '+i][1][0]*scale[0]
    return offset_turn


def draw_string(screen, string=str, pos=(0, 0, 0), scale=(1, 1), color=(255, 255, 255, 255), alignment='right'):
    offset_turn = 0
    for i in string:
        screen.draw_texture(image_dict['font '+i][0], (pos[0]+offset_turn * scale[0]-(0 if alignment == 'right' else sum([image_dict['font '+n][1][0]for n in string])
                                                                                      * scale[0]), pos[1], pos[2]), (image_dict['font '+i][1][0]*scale[0], image_dict['font '+i][1][1]*scale[1]), (False, False), color, [0, 0, 0], False, 1)
        offset_turn += image_dict['font '+i][1][0]


mirror_pad = {'1': '3', '3': '1', '4': '6', '6': '4', '7': '9', '9': '7', '12': '32', '13': '31', '14': '36', '15': '35', '16': '34', '17': '39', '18': '38', '19': '37', '21': '23', '23': '21', '24': '26', '26': '24', '27': '29', '29': '27', '31': '13', '32': '12', '34': '16', '35': '15', '36': '14', '37': '19', '38': '18', '39': '17', '41': '63', '42': '62', '43': '61', '45': '65', '46': '64', '47': '69', '48': '68', '49': '67',
              '51': '53', '53': '51', '54': '56', '56': '54', '57': '59', '59': '57', '61': '43', '62': '42', '63': '41', '64': '46', '65': '45', '67': '49', '68': '48', '69': '47', '71': '93', '72': '92', '73': '91', '74': '96', '75': '95', '76': '94', '78': '98', '79': '97', '81': '83', '83': '81', '84': '86', '86': '84', '87': '89', '89': '87', '91': '73', '92': '72', '93': '71', '94': '76', '95': '75', '96': '74', '97': '79', '98': '78'}


def get_command(self, state=[]):
    state = [self.current_state, 'crouch' if self.boxes['hurtbox'].get(
        'crouch') != None else 'stand']+state
    for move in self.command_index_timer:
        for index in range(len(self.command_index_timer[move])):

            input_gate = [mirror_pad.get(l, l) for l in object_dict[self.name]['moveset'][move]['command'][index][self.command_index_timer[move][index][0]].split(",")]if (
                self.other_main_object.pos[0]-self.pos[0]) < 0 else object_dict[self.name]['moveset'][move]['command'][index][self.command_index_timer[move][index][0]].split(",")

            intersection = 0
            for input in input_gate:
                if ('|' in input and set(input.split("|")) & set(state)) or ('!' in input and input.split("!")[1] not in state) or (input in state):
                    intersection += 1

            if intersection >= len(input_gate):
                self.command_index_timer[move][index] = [self.command_index_timer[move][index]
                                                         [0]+1, object_dict[self.name]['moveset'][move].get('command_link_time', 14)]
                if self.command_index_timer[move][index][0] >= len(object_dict[self.name]['moveset'][move]['command'][index]):
                    self.buffer_state[move], self.command_index_timer[move][index] = object_dict[self.name]['moveset'][move].get('buffer', 1), [
                        0, 0]


def get_state(self, buffer={}, force=0):
    for move in {m: buffer[m] for m in object_dict[self.name]['moveset'] if m in buffer}:
        if force or (self.fet in object_dict[self.name]['moveset'][move].get('state', 'grounded') and ((self.frame == [0, 0] or (('kara' in object_dict[self.name]['moveset'][move].get('cancel', ["neutral"]) and self.kara and 'kara'not in object_dict[self.name]['moveset'][self.current_state].get('cancel', ["neutral"])) or (set(self.cancel).intersection(object_dict[self.name]['moveset'][move].get('cancel', ["neutral"])))))) and self.gauges.get('pressure', 0) >= object_dict[self.name]['moveset'][move].get('use pressure', 0)):
            if object_dict[self.name]['moveset'][move].get('use pressure', 0):
                self.gauges['pressure'] -= object_dict[self.name]['moveset'][move]['use pressure']
            self.current_state, self.boxes, self.frame, self.kara, self.buffer_state, self.acceleration, self.con_speed, self.hitstun, self.repeat = move, dict(
                object_dict[self.name]['boxes']), [len(object_dict[self.name]['moveset'][move]['framedata']), 0], 2, {}, [0, 0], [0, 0], -1 if ('ummble' in move and self.fet == 'airborne')else self.hitstun, 0

            return True
    return False


def next_frame(self, state):
    state = default_substate | state
    if self.frame[0] <= 0:
        self.frame = [0, 0]
        return
    self.image_size, self.image_offset, self.image_mirror, self.image_tint, self.image_angle, self.image_repeat, self.image_glow, self.ignore_stop, self.hold_on_stun, self.cancel = object_dict[
        self.name]['def_image_size'], object_dict[self.name]['def_image_offset'], [False, False], (255, 255, 255, 255), (0, 0, 0), False, False, False, False, [None]
    for value in function_dict:
        if state.get(value, None) != None:
            function_dict[value](self, state[value], False)
    self.frame[0] -= 1


def object_kill(self, *args):
    """Kill the object instantly."""
    try:
        object_list.remove(self)
    except:
        pass


def object_remove_box_key(self=object, key='', *args):
    self.boxes[key[0]].pop(key[1], None)


def object_hitset(self, hitset=any, *args):
    """Enable collisions of the current hitbox, it stays at 1 and after a hit it goes back to 0."""
    self.boxes['hitbox']['hitset'] = self.boxes['hitbox'].get('hitset', 1)-1


def object_hit_damage(self: object, damage=(10, 0), other=object, *args):
    """Damage done to the object that has been hit. Damage on Parry is 0. 'damage':(Damage on hit, Damage on block)"""
    damage = math.ceil(abs({'parry': 0, 'block': damage[1]*(self.self_main_object.damage_scaling[0]if self.self_main_object.damage_scaling[0] > self.self_main_object.damage_scaling[1]else self.self_main_object.damage_scaling[1])/100, 'hurt': damage[0]*(
        self.self_main_object.damage_scaling[0]if self.self_main_object.damage_scaling[0] > self.self_main_object.damage_scaling[1]else self.self_main_object.damage_scaling[1])/100}.get(other.current_command[0], 0)))
    other.gauges['health'], other.last_damage = other.gauges['health'] - \
        damage, [other.last_damage[0] +
                 damage if other.hitstun else damage, damage]


def object_hit_hitgain(self: object, gain=(5, 0), other=object, *args):
    """Special bar Gain, applies to the object that hits and the object hit. Gain on Parry is 0. 'Gain':(Gain on hit, Gain on block)"""
    self.gauges['pressure'] += {'parry': 0, 'block': gain[0]
                                [1], 'hurt': gain[0][0]}.get(other.current_command[0], 0)
    other.gauges['pressure'] += {'parry': 8, 'block': gain[1]
                                 [1], 'hurt': gain[1][0]}.get(other.current_command[0], 0)


def object_hit_stamina(self: object, stamina=(0, 0), other=object, *args):
    """Stamina lost by the object hit. Stamina lost on Parry is 0. 'Stamina':(Stamina lost on hit, Stamina loston block)"""
    other.gauges['stamina'] += {'parry': 0, 'block': stamina[1],
                                'hurt': stamina[0]}.get(other.current_command[0], 0)


def object_hit_hitstun(self: object, stun=(30, 0), other=object, *args):
    """Hitstun of the object that has been hit. Hitstun on Parry is 0. 'Hitstun':(Hitstun on hit, Hitstun on block)"""
    other.hitstun = {'hurt': stun[0], 'block': stun[1], 'parry': 0}.get(
        other.current_command[0], 0)  # hitstun


def object_hit_hitstop(self: object, stop=10, other=object, *args):
    """Hitstop (Hitlag) of the hitting object and the object that has been hit. It depends on whether it is a hit, block or parry. The Hitstop advantage on parry varies for Normal, Special or Super attacks. 'Hitstop': Stop on frames"""
    tipe = 'parry' in [
        tipe for tipe in attack_tipe_value if tipe in other.current_command]
    self.hitstop, other.hitstop = 16 if tipe else stop, 16 if tipe else stop

    object_display_shake(other, [20*self.face if tipe else other.speed[0], 0 if tipe else other.speed[1],
                                 self.hitstop if tipe else other.hitstop, 'other' if tipe else 'self'], self)

    object_display_shake(get_object_per_team(self.team, False, 'Combo_Counter'), [
        other.speed[0], other.speed[1], 20, 'self'], self)


def object_hit_juggle(self: object, juggle: int = 1, other=object, *args):
    """Indicates how many hits an object can withstand while airborne. When the counter is less than 0, the hit object becomes intangible until it hits the ground. 'Juggle': Juggle number subtracted"""
    if other.fet == 'airborne':
        other.juggle -= int(juggle)


def object_hit_knockback(self: object, knockback={"grounded": [14, 0]}, other=object, *args):
    """The recoil of the on the object being hit. Knockback on Parry is 0. 'Knockback':(Knockback on block (X, Y), Knockback on hit (X, Y), Knockback while airborne (X, Y))"""
    speed = list(knockback.get("grounded", [14, 0]))
    if "hurt" in other.current_command[0] and knockback.get("airborne", False) and other.fet == 'airborne':
        speed = list(knockback['airborne'])
    if "block" in other.current_command[0]:
        speed = list(knockback['block'])if knockback.get(
            "block", False)else [speed[0], 0]
    if "parry" in other.current_command[0]:
        speed = list(knockback['parry'])if knockback.get(
            "parry", False)else [0, 0]
    speed[0] = speed[0]*self.face
    other.speed, other.fet, other.face, other.pos[1] = speed, 'airborne' if speed[1] > 0 and other.fet == 'grounded' else 'grounded', 1 if self.self_main_object.pos[
        0] > other.pos[0] else -1, other.pos[1]-(10 if speed[1] > 0 and other.fet == 'grounded' else 0)


def object_hit_hittipe(self: object, hittipe: list = ['medium', 'middle'], other: object = object, *args):
    """Determines the type of hit. Super, Special, Heavy, Medium or Light. High, Mid or Low. A specific hit type can be added to initiate a unique hit animation. 'Hittipe': [hit tipe 1, hit tipe 2,,, hit tipe N]"""
    self.damage_scaling, other.frame = [self.self_main_object.damage_scaling[0]-attack_tipe_value[[tipe for tipe in attack_tipe_value if tipe in hittipe]
                                                                                                  [0]]['scaling'], attack_tipe_value[[tipe for tipe in attack_tipe_value if tipe in hittipe][0]]['min_scaling']], [0, 0]
    if 'hurt' in other.current_command:
        other.current_command, other.cancel, other.pos[1] = other.current_command+list(
            hittipe), [None], other.pos[1]-1 if other.fet == 'grounded' and self.boxes['hitbox']['knockback'].get("grounded", [14, 0])[1] else other.pos[1]


def object_wallbounce(self: object, wallbounce=1, other=object, *args):
    """Indicates whether the hit object will bounce off walls. 'Wallbounce': Any"""
    other.wallbounce = True


def object_duration(self: object, d=0, *args):
    """The duration of the substate in frames. 'dur': duration"""
    self.frame[1] = d


def object_image(self: object, image='reencor/none', *args):
    """Name of the image displayed. It corresponds to the name of the folder followed by '/' and followed by the name of the image file. 'image': 'Name'"""
    image_id, image_size = image_dict.get(
        str(image), (image_dict['reencor/none'][0], [0, 0]))
    self.image, self.real_image_size = image_id, image_size


def object_image_size(self: object, size=[10, 10], *args):
    """Name of the image displayed. It corresponds to the name of the folder followed by '/' and followed by the name of the image file. 'image': 'Name'"""
    self.image_size = size


def object_image_offset(self: object, image_offset=[0, 0], *args):
    """image Temporal Offset. Only during the current substate. 'image_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.image_offset = image_offset


def object_image_mirror(self: object, m=(0, 0), *args):
    """Reflects the last loaded image. 'image_mirror': (X image_mirror 1 if true, Y image_mirror 1 if true)"""
    self.image_mirror = m


def object_image_tint(self: object, tint=(255, 255, 255, 255), *args):
    self.image_tint = tint


def object_image_angle(self: object, angle=(0, 0, 0), *args):
    self.image_angle = angle


def object_image_repeat(self: object, repeat=False, *args):
    self.image_repeat = repeat


def object_image_glow(self: object, glow=0, *args):
    self.image_glow = glow


def GL_set_light(self, light=[-1, 1, -2, 0], *args):
    glLightfv(GL_LIGHT0, GL_POSITION, light)


def GL_set_ambient(self, ambient=[.9, .9, .9, 1], *args):
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)


def object_display_shake(self: object, shake=[0, 0, 0, None], other=object, *args):
    shake[0], shake[1] = normalize_vector(shake[0], shake[1], 20)
    if shake[3] == 'self':
        self.draw_shake = [0, 0, 0, shake[0], shake[1], shake[2]]
    if shake[3] == 'other':
        other.draw_shake = [0, 0, 0, shake[0], shake[1], shake[2]]
    if shake[3] == 'camera':
        game = get_object_per_class_ev("GameObject")
        game.camera.draw_shake = [0, 0, 0, shake[0], shake[1], shake[2]]


def object_double_image(self: object, doim=any, *args):
    """Draw the above images on the screen. 'Double_image': Any"""
    pass


def object_voice(self: object, voice='reencor/nota', *args):
    """Plays sound from the object. This sound can be interrupted. 'folder/file name'. 'Voice': 'Name'"""
    voice = sound_dict.get(weighted_choice(voice), 'none')
    if voice != 'none':
        self.voice_channel.play(voice)
    else:
        pass


def object_sound(self: object, sound='reencor/nota', *args):
    """Plays sound from the object. This sound can not be interrupted. 'folder/file name'. 'Sound': 'Name'"""
    sound = sound_dict.get(sound, 'none')
    if sound != 'none':
        self.sound_channel.play(sound)
    else:
        pass


def object_facing(self: object, facing=1, *args):
    """Set the direction in which the object is facing. 'Facing': -1 reverses the direction the object is currently facing"""
    self.face *= facing


def object_pos_offset(self: object, pos_offset=(0, 0), *args):
    """Changes the location of the object instantly. Does not affect speed. 'Pos_offset': (X Offset (Depends on where the object is facing), Y Offset)"""
    self.pos = [self.pos[0]+pos_offset[0]*self.face,
                self.pos[1]-pos_offset[1], self.pos[2]]


def object_speed(self: object, speed=(0, 0), *args):
    """Set the absolute Speed of the object. 'Speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    self.speed = [speed[0]*self.face, speed[1]]


def object_acceleration(self: object, accel=(0, 0), *args):
    """Set the Acceleration of the object. 'Accel': (X Acceleration (Depends on where the object is facing)., Y Acceleration)"""
    self.acceleration = accel[0], accel[1]


def object_add_speed(self: object, add_speed=(0, 0), *args):
    """Adds Speed to the object. 'Add_speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    self.speed = [self.speed[0]+add_speed[0] *
                  self.face, self.speed[1]+add_speed[1]]


def object_con_speed(self: object, con_speed=(0, 0), *args):
    """Set the Speed of the object during all the current state. 'Con_speed': (X Speed (Depends on where the object is facing)., Y Speed)"""
    self.con_speed = [con_speed[0]*self.face, con_speed[1]]


def object_cancel(self: object, cancel=0, *args):
    """Set the Cancel State of the object during all the current state. 'Cancel': Any"""
    if isinstance(cancel, str):
        cancel = [cancel]
    self.cancel = cancel


def object_main_cancel(self: object, cancel=0, *args):
    """Set the Cancel State of the object during all the current state. 'Cancel': Any"""
    if isinstance(cancel, str):
        cancel = [cancel]
    self.self_main_object.cancel = cancel


def object_ignore_stop(self: object, *args):
    """Ignore the Stop or Hitstop. 'Ignore_stop': Any"""
    self.ignore_stop = True


def object_hold_on_stun(self: object, *args):
    """Hold_on_stun. 'hold_on_stun': Any"""
    self.hold_on_stun = True


def object_smear(self: object, image='reencor/none', *args):
    """Changes the current substate image to simulate a Smear. 'Smear': Any"""
    c = self.cancel
    next_frame(self, object_dict[self.name]['moveset']
               [self.current_state]['framedata'][-self.frame[0]])
    self.cancel = c


def object_gain(self: object, gain=0, *args):
    """Special bar Gain, applies only to the object that hits. Gain on Parry is 0. 'Gain': Number"""
    self.gauges['pressure'] += gain
    # reward_on(self,1)


def object_superstop(self, superstop=1, *args):
    """The Stop applies to all currently active objects. 'Superstop': Number"""
    for object in object_list:
        if object.__class__.__name__ in ('CharacterActiveObject', 'ProjectileActiveObject', 'StageActiveObject'):
            object.hitstop += superstop


def object_camera_path(self: object, camera_path=(), *args):
    """The path the camera will follow. 'Camera_path': ()"""
    game = get_object_per_class_ev("GameObject")
    game.camera_path, game.frame = {'path': tuple(camera_path['path']), 'object': {
        'self': self.self_main_object, 'other': self.other_main_object, 'global': game}[camera_path['object']]}, [0, 0]


def object_hurtbox(self: object, hurtbox={'boxes': []}, *args):
    """The boxes on an object that indicate where it can be hit."""
    self.boxes['hurtbox'] = dict(
        object_dict[self.name]['boxes']['hurtbox'] | hurtbox)


def object_hitbox(self: object, hitbox={'boxes': []}, *args):
    """The boxes on an object that indicate where can it hit."""
    self.boxes['hitbox'] = dict(
        object_dict[self.name]['boxes']['hitbox'] | hitbox)


def object_grabbox(self: object, grabbox={'boxes': []}, *args):
    """The boxes on an object that indicate where can it grab."""
    self.boxes['grabbox'] = dict(
        object_dict[self.name]['boxes']['grabbox'] | grabbox)


def object_pushbox(self: object, pushbox={'boxes': []}, *args):
    """The boxes on an object that indicate where it can be pushed."""
    self.boxes['pushbox'] = dict(
        object_dict[self.name]['boxes']['pushbox'] | pushbox)


def object_takebox(self: object, takebox={'boxes': []}, *args):
    """The boxes on an object that indicate where it can be grabed."""
    self.boxes['takebox'] = dict(
        object_dict[self.name]['boxes']['takebox'] | takebox)


def object_triggerbox(self: object, triggerbox={'boxes': []}, *args):
    """The boxes on an object that indicate where it can be triggered."""
    self.boxes['triggerbox'] = dict(
        object_dict[self.name]['boxes']['triggerbox'] | triggerbox)


def object_boundingbox(self: object, boundingbox={'boxes': []}, *args):
    """The boxes on an object that indicate the limmits."""
    self.boxes['boundingbox'] = dict(
        object_dict[self.name]['boxes']['boundingbox'] | boundingbox)


def object_boxes(*args):
    """List of boxes for each of the box types. Not needed outside of box types."""
    pass


def object_update_box(self=object, update_box={}, *args):
    for box in update_box:
        self.boxes[box] = self.boxes.get(box, {}) | update_box[box]


def object_guard(self: object, guard=['middle', 0], *args):
    """Set the Parry State of the object during all the current substate hurtbox. 'Guard': Any"""
    pass


def object_repeat_substate(self: object, repeat_substate=0, *args):
    """Repeat from the specified substate within the current state."""
    if self.repeat < repeat_substate[1] or repeat_substate[1] == -1:
        self.frame, self.repeat = [self.frame[0] +
                                   repeat_substate[0], 0], self.repeat + 1
    if self.repeat == repeat_substate[1]:
        self.frame = [self.frame[0], 0]


def object_get_state(self: object, command=[], *args):
    """Updates the current state by searching through a state buffer."""
    get_command(self, self.current_command +
                list(self.inputdevice.current_input)+command)
    got_state = get_state(self, self.buffer_state)
    if got_state:
        next_frame(self, object_dict[self.name]['moveset']
                   [self.current_state]['framedata'][-self.frame[0]])


def object_other_get_state(self: object, command=[], other=object, *args):
    """Updates the current state by searching through a state buffer."""
    get_command(other, other.current_command+list(other.inputdevice.current_input) +
                [self.name, self.current_state]+command)
    got_state = get_state(other, other.buffer_state)
    if got_state:
        next_frame(other, object_dict[other.name]['moveset']
                   [other.current_state]['framedata'][-other.frame[0]])


def object_random_state(self: object, random_state={'Stand': {'chance': 1}}, *args):
    """Updates the state instantly using the State Name."""
    state = weighted_choice(random_state)
    if object_dict[self.name]['moveset'].get(state) != None:
        self.current_state, self.boxes, self.frame = state, dict(object_dict[self.name]['boxes']), [
            len(object_dict[self.name]['moveset'][state]['framedata']), 0]
        next_frame(self, object_dict[self.name]['moveset']
                   [self.current_state]['framedata'][-self.frame[0]])


def object_trigger_state(self: object, state='Stand', *args):
    """Updates the state instantly using the State Name."""
    if object_dict[self.name]['moveset'].get(state) != None:
        self.current_state, self.boxes, self.frame = state, dict(object_dict[self.name]['boxes']), [
            len(object_dict[self.name]['moveset'][state]['framedata']), 0]
        next_frame(self, object_dict[self.name]['moveset']
                   [self.current_state]['framedata'][-self.frame[0]])


def object_influence(self: object, who=None, other=object, *args):
    if who == 'other':
        self.object_influence, other.grabed = other, self
    elif who == 'global':
        game = get_object_per_class('GameObject')
        self.object_influence, other.grabed = other, game
    elif who == 'camera':
        camera = get_object_per_class('Camera')
        self.object_influence, other.grabed = other, camera


def object_influence_pos(self, pos=[10, 10, 10], *args):
    if self.object_influence != None:
        self.object_influence.pos = [
            self.pos[0]+pos[0]*self.face, self.pos[1]-pos[1], 0]


def object_influence_speed(self, speed=[10, 10], *args):
    if self.object_influence != None:
        self.object_influence.speed = [speed[0]*self.face, speed[1]]


def object_off_influence(self: object, *args):
    self.object_influence.grabed = None
    self.object_influence = None


def object_stop(self: object, stop=0, *args):
    """Sets the Hitstop of the current object."""
    self.hitstop = stop


def object_create_VisualEffectObject(self: object, o=(), *args):
    """Creates a new object, projectile or any other kind of object."""
    from Util.Active_Objects import VisualEffectObject
    object_list.append(VisualEffectObject(
        o[0], (self.pos[0]+o[1][0]*self.face, self.pos[1]-o[1][1]), self.face*o[2], o[3], o[4]))


def object_create_ProjectileActiveObject(self: object, o=(), *args):
    """Creates a new object, projectile or any other kind of object."""
    from Util.Active_Objects import ProjectileActiveObject
    object_list.append(ProjectileActiveObject(self.team, self.inputdevice, o[0], (
        self.pos[0]+o[1][0]*self.face, self.pos[1]-o[1][1]), self.face*o[2], o[3], o[4]))


function_dict = {
    'remove_box_key': object_remove_box_key,

    'hitset': object_hitset,  # reset hitbox hit state
    'damage': object_hit_damage,  # damage
    'knockback': object_hit_knockback,  # knockback on object
    'hitstop': object_hit_hitstop,  # hitstop
    'hitstun': object_hit_hitstun,  # hitstun
    'stamina': object_hit_stamina,  # stun bar or stamina
    'hit pressure': object_hit_hitgain,  # bar gain
    'hittipe': object_hit_hittipe,  # hit type force, style
    'juggle': object_hit_juggle,
    'wallbounce': object_wallbounce,

    'dur': object_duration,  # duration in frames #dict

    'image': object_image,  # image image #dict
    'image_size': object_image_size,  # current image offset #dict
    'image_offset': object_image_offset,  # current image offset #dict
    'image_mirror': object_image_mirror,  # image image_mirror #function
    'image_tint': object_image_tint,
    'image_angle': object_image_angle,
    'image_repeat': object_image_repeat,
    'image_glow': object_image_glow,
    'double_image': object_double_image,
    'draw_shake': object_display_shake,

    'light': GL_set_light,
    'ambient': GL_set_ambient,
    'music': nomatch,

    'voice': object_voice,  # current image offset #function
    'sound': object_sound,

    'facing': object_facing,  # facing #dict
    'pos_offset': object_pos_offset,  # offset object pos in first frame #dict
    'speed': object_speed,  # speed #dict
    'accel': object_acceleration,  # acceleration #dict
    'add_speed': object_add_speed,  # acceleration #dict
    'con_speed': object_con_speed,  # acceleration #dict

    'cancel': object_cancel,  # cancelable #dict
    'main_cancel': object_main_cancel,
    'guard': object_guard,
    'ignore_stop': object_ignore_stop,  # ignore hitstop #dict
    'hold_on_stun': object_hold_on_stun,  # ignore hitstop #dict
    'smear': object_smear,  # ignore hitstop #dict
    'pressure': object_gain,  # ignore hitstop #dict

    'superstop': object_superstop,  # stop in every object except self
    'camera_path': object_camera_path,  # camera path and zoom

    'hurtbox': object_hurtbox,  # hurtbox data #dict
    'hitbox': object_hitbox,  # hitbox data #dict
    'grabbox': object_grabbox,  # grabbox data #dict
    'pushbox': object_pushbox,  # create pushbox #dict
    'takebox': object_takebox,  # create takebox #dict
    'triggerbox': object_triggerbox,  # create takebox #dict
    'boundingbox': object_boundingbox,
    'boxes': object_boxes,  # hitbox size
    'update_box': object_update_box,

    'influence': object_influence,
    'influence_pos': object_influence_pos,
    'influence_speed': object_influence_speed,
    'off_influence': object_off_influence,

    'repeat_substate': object_repeat_substate,  # go back n frames #function
    'get_state': object_get_state,  # cancel to next move #function
    'other_get_state': object_other_get_state,
    'trigg_state': object_trigger_state,
    'random_state': object_random_state,

    'stop': object_stop,  #

    # object generation #function
    'create_VisualEffectObject': object_create_VisualEffectObject,
    # object generation #function
    'create_ProjectileActiveObject': object_create_ProjectileActiveObject,

    'kill': object_kill,  # destroy object

}
